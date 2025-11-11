# src/run_full_pipeline.py
from src.schema_fetcher import extract_all
from src.vector_store import upsert_table_docs
from src.rag_query import question_to_sql_and_execute
import json
import argparse
from datetime import date, datetime
from decimal import Decimal

# ---------------------------------------------------------------------
# Utility: Safe JSON serialization (for date, datetime, Decimal, etc.)
# ---------------------------------------------------------------------
def safe_json(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    return str(o)


# ---------------------------------------------------------------------
# Step 1: Build + Index schema
# ---------------------------------------------------------------------
def build_and_index(sample_n: int = 5):
    """
    Extract schema from MySQL, create embeddings, and upsert into Chroma DB.
    """
    docs = extract_all(sample_n)
    print(f"Extracted {len(docs)} table docs. Upserting to vector store...")
    res = upsert_table_docs(docs)
    print("✅ Upsert result:", res)


# ---------------------------------------------------------------------
# Step 2: Ask natural language → SQL → Execute → Return rows
# ---------------------------------------------------------------------
def ask(question: str):
    """
    Query the indexed schema with a natural language question.
    Generates SQL, executes it safely, and prints results.
    """
    print(f"\n🧠 Question: {question}\n")
    out = question_to_sql_and_execute(question, run_query=True)

    print("💬 Generated SQL:\n", out["sql"], "\n")

    if out.get("rows") is not None:
        try:
            print("📊 Rows:\n", json.dumps(out["rows"], indent=2, default=safe_json))
        except Exception as e:
            print(f"⚠️ Could not serialize rows to JSON: {e}")
            print("Raw rows:", out["rows"])
    else:
        print("⚠️ No rows returned.")

    return out


# ---------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LangChain NL2SQL Chatbot Backend Pipeline")
    parser.add_argument("--build", action="store_true", help="Extract schema and upsert embeddings into Chroma")
    parser.add_argument("--ask", type=str, help="Ask a natural language question to the database")
    parser.add_argument("--sample_n", type=int, default=5, help="Number of tables to sample from the schema")
    args = parser.parse_args()

    if args.build:
        build_and_index(args.sample_n)
    if args.ask:
        ask(args.ask)
