# src/sql_executor.py
from sqlalchemy import create_engine, text
from src.config import DB_URI
import re
from sqlalchemy.exc import SQLAlchemyError

RO_SCHEMA = DB_URI  # For prod use a read-only user/replica

engine = create_engine(RO_SCHEMA, pool_pre_ping=True, future=True)

SELECT_RE = re.compile(r"^\s*SELECT\s", re.IGNORECASE)

# def safe_prepare_query(sql: str, limit: int = 1000) -> str:
#     # Basic validation: only SELECT allowed
#     if not SELECT_RE.match(sql):
#         raise ValueError("Only SELECT queries allowed in safe executor.")
#     # If query already has LIMIT, return as-is (we could try to increase or reduce)
#     if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE):
#         return sql
#     # Append a limit
#     return sql.strip().rstrip(";") + f" LIMIT {limit};"
def safe_prepare_query(sql: str, limit: int = 1000) -> str:
    """
    Ensures only safe SELECT queries are executed.
    Adds a LIMIT if not present.
    """
    sql_clean = sql.strip().strip("`").strip(";")
    sql_clean = sql_clean.replace("```", "").replace("SQL", "").replace("sql", "").strip()

    # extract only the part after the last 'select' to avoid preceding commentary
    lower_sql = sql_clean.lower()
    if "select" not in lower_sql:
        raise ValueError("Only SELECT queries allowed in safe executor.")

    select_start = lower_sql.find("select")
    sql_clean = sql_clean[select_start:].strip()

    if not sql_clean.lower().startswith("select"):
        raise ValueError("Only SELECT queries allowed in safe executor.")

    # Ensure LIMIT is present
    if "limit" not in lower_sql:
        sql_clean = sql_clean.rstrip(";") + f" LIMIT {limit};"

    return sql_clean


def run_select(sql: str, limit: int = 1000):
    q = safe_prepare_query(sql, limit)
    try:
        with engine.connect() as conn:
            q = q.replace("```sql", "").replace("```", "").replace("---", "").strip() #added new 
            res = conn.execute(text(q))
            rows = [dict(r) for r in res.mappings().all()]
        return rows
    except SQLAlchemyError as e:
        raise RuntimeError(f"Query failed: {e}")
