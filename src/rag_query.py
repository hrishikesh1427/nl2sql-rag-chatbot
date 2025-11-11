# src/rag_query.py
import os
import re
from typing import Tuple
from openai import OpenAI
from src.vector_store import similarity_search
from src.sql_executor import run_select

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# ------------------------- FEW-SHOT EXAMPLES -------------------------
FEW_SHOT_EXAMPLES = """
Example 1:
User question: List all employee names and their departments.
SQL: SELECT e.name, d.name AS department_name
     FROM employees e
     JOIN departments d ON e.department_id = d.id;

Example 2:
User question: Find the total sales amount per customer.
SQL: SELECT c.name AS customer_name, SUM(o.total_amount) AS total_sales
     FROM customers c
     JOIN orders o ON c.id = o.customer_id
     GROUP BY c.name;

Example 3:
User question: Get the average salary of employees in each department.
SQL: SELECT d.name AS department_name, AVG(e.salary) AS avg_salary
     FROM employees e
     JOIN departments d ON e.department_id = d.id
     GROUP BY d.name;
Example 4:
User question: Fetch top 5 most ordered items.
SQL: SELECT p.id AS product_id, p.name AS product_name, COUNT(oi.id) AS order_count
     FROM order_items oi
     JOIN products p ON oi.product_id = p.id
     GROUP BY p.id, p.name
     ORDER BY order_count DESC
     LIMIT 5;

"""

# ------------------------- PROMPT TEMPLATE -------------------------
PROMPT_TEMPLATE = f"""
You are a SQL assistant that generates **accurate, readable MySQL SELECT** queries.

Here are examples of correct queries:
{FEW_SHOT_EXAMPLES}

---

Schema context:
{{table_info}}

User question: {{user_question}}

Guidelines:
- Only output one valid SQL SELECT query.
- Do not include any explanation, reasoning, or markdown.
- Prefer aggregating/counting from the table that directly represents the user verb (e.g. use order_items for "ordered", orders for "orders", inventory for "stock/received").
- Avoid joins to auxiliary tables (inventory/products) unless needed for requested columns.
- If user asks about "most ordered", "top-selling", or "ordered count", use order_items as the primary table and then join products only to get names.
- Do not add extra joins that can filter results unnecessarily.
- Output must begin directly with SELECT and end with a semicolon.
-If you cannot determine the query confidently, still produce your best possible SELECT query instead of giving advice or instructions.
Never return explanations, hints, or commentary — only the SQL statement.
"""

# ------------------------- RETRIEVAL -------------------------
def assemble_table_info(question: str, k: int) -> Tuple[str, list]:
    docs = similarity_search(question, k=k)
    seen = set()
    parts = []
    tables_used = []
    for d in docs:
        t = d["metadata"].get("table")
        tables_used.append(t)
        if t not in seen:
            seen.add(t)
            parts.append(f"---\n{d['text']}\n")
    print(f"🔎 assemble_table_info: top docs/tables used = {tables_used}")
    return "\n".join(parts), docs


# ------------------------- LLM CALL -------------------------
def call_llm(prompt: str, max_tokens: int = 256, temperature: float = 0.0):
    """Call the LLM (chat or text completion fallback)."""
    try:
        resp = openai_client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"), 
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].message["content"]
    except Exception:
        resp = openai_client.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].text

# ------------------------- MAIN PIPELINE -------------------------
def question_to_sql_and_execute(user_question: str, run_query: bool = True):
    """Full RAG pipeline: retrieve schema context, call LLM, extract & execute SQL."""

    # Dynamically adjust number of retrieved schema chunks
    word_count = len(user_question.split())
    k = 8 if word_count < 15 else 12
    print(f"📚 Retrieved top {k} schema chunks for LLM context.\n")

    # Step 1: Retrieve schema info for context
    table_info, docs = assemble_table_info(user_question, k=k)
    prompt = PROMPT_TEMPLATE.format(table_info=table_info, user_question=user_question)
    
    # Step 2: Get LLM output
    raw_output = call_llm(prompt).strip()
    # 🧩 If LLM returns only advice or no SELECT, retry once with simpler phrasing
    if "select" not in raw_output.lower():
        print("⚠️ LLM returned advice instead of SQL. Retrying...")
        retry_prompt = prompt + "\nNow output only the SQL query."
        raw_output = call_llm(retry_prompt).strip()


    # Step 3: Clean up markdown/code fences
    cleaned = (
        raw_output.replace("```sql", "")
        .replace("```", "")
        .replace("---", "")
        .strip()
    )

    # Step 4: Extract only the first valid SQL block (ignore explanations)
    sql_match = re.search(
        r"(?i)(SELECT[\s\S]+?)(?:;|\n\s*(?:###|#|--|$))", cleaned
    )
    if sql_match:
        sql_text = sql_match.group(1).strip() + ";"
    else:
        raise ValueError(f"No valid SQL found in LLM output:\n{raw_output}")

    # Step 5: Remove any extra commentary lines after SQL
    lines = []
    for line in sql_text.splitlines():
        if any(line.strip().startswith(x) for x in ["#", "###", "--"]):
            break
        lines.append(line)
    sql_text = "\n".join(lines).strip()

    # Debug print
    print(f"\n🧠 Generated SQL:\n{sql_text}\n")
# 🪶 Log every generated SQL query to a file for debugging
    log_entry = f"\n---\nQuestion: {user_question}\nGenerated SQL:\n{sql_text}\n---\n"
    with open("generated_queries.log", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)

    # Step 6: Execute safely
    if run_query:
        rows = run_select(sql_text, limit=1000)
        return {"sql": sql_text, "rows": rows, "sources": docs}
    else:
        return {"sql": sql_text, "rows": None, "sources": docs}
