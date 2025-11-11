# src/schema_fetcher.py
import hashlib
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from src.config import DB_URI
import pandas as pd

engine = create_engine(DB_URI, pool_pre_ping=True, future=True)

def compute_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def list_tables(schema: str = None):
    schema = schema or engine.url.database
    q = text("""
      SELECT TABLE_NAME, TABLE_TYPE, ENGINE, TABLE_ROWS, CREATE_TIME
      FROM information_schema.tables
      WHERE TABLE_SCHEMA = :db
    """)
    with engine.connect() as conn:
        res = conn.execute(q, {"db": schema}).mappings().all()
    return [dict(r) for r in res]

def get_columns(table: str, schema: str = None):
    schema = schema or engine.url.database
    q = text("""
      SELECT COLUMN_NAME, ORDINAL_POSITION, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
      FROM information_schema.columns
      WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table
      ORDER BY ORDINAL_POSITION
    """)
    with engine.connect() as conn:
        res = conn.execute(q, {"db": schema, "table": table}).mappings().all()
    return [dict(r) for r in res]

def get_foreign_keys(table: str, schema: str = None):
    schema = schema or engine.url.database
    q = text("""
      SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
      FROM information_schema.key_column_usage
      WHERE TABLE_SCHEMA = :db AND TABLE_NAME = :table AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    with engine.connect() as conn:
        res = conn.execute(q, {"db": schema, "table": table}).mappings().all()
    return [dict(r) for r in res]

def get_indexes(table: str):
    q = text(f"SHOW INDEX FROM `{engine.url.database}`.`{table}`")
    with engine.connect() as conn:
        try:
            res = conn.execute(q).mappings().all()
            return [dict(r) for r in res]
        except Exception:
            return []

def sample_rows(table: str, n: int = 5):
    q = text(f"SELECT * FROM `{table}` LIMIT :n")
    with engine.connect() as conn:
        try:
            df = pd.read_sql(q, conn, params={"n": n})
            return df.fillna("").astype(str).to_dict(orient="records")
        except Exception:
            return []

def build_table_doc(table_meta: dict, sample_n: int = 5) -> dict:
    table = table_meta["TABLE_NAME"]
    cols = get_columns(table)
    fks = get_foreign_keys(table)
    idxs = get_indexes(table)
    samples = sample_rows(table, sample_n)
    parts = []
    parts.append(f"Table: {table}")
    parts.append(f"Engine: {table_meta.get('ENGINE')} Rows(estimate): {table_meta.get('TABLE_ROWS')}")
    parts.append("Columns:")
    for c in cols:
        parts.append(f"- {c['COLUMN_NAME']}: {c['COLUMN_TYPE']} nullable={c['IS_NULLABLE']} key={c['COLUMN_KEY']} extra={c['EXTRA']}")
    if fks:
        parts.append("Foreign Keys:")
        for fk in fks:
            parts.append(f"- {fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
    if idxs:
        parts.append("Indexes:")
        for idx in idxs:
            parts.append(f"- {idx.get('Key_name')} unique={bool(idx.get('Non_unique')==0)} cols={idx.get('Column_name')}")
    if samples:
        parts.append(f"Sample rows (first {len(samples)}):")
        for r in samples:
            parts.append(json.dumps(r, default=str))
    full_text = "\n".join(parts)
    return {
        "table": table,
        "db": engine.url.database,
        "text": full_text,
        "schema_hash": compute_hash(full_text),
        "created_at": datetime.utcnow().isoformat(),
        "columns": cols,
        "fks": fks,
        "samples": samples
    }

# def extract_all(sample_n: int = 5):
#     tables = list_tables()
#     docs = []
#     for t in tables:
#         docs.append(build_table_doc(t, sample_n))
#     return docs
def extract_all(sample_n: int = 5, skip_system: bool = True):
    schema = engine.url.database
    tables = list_tables(schema)
    total = len(tables)
    print(f"📦 Found {total} tables in database '{schema}'")

    docs = []
    for i, t in enumerate(tables, start=1):
        name = t["TABLE_NAME"]
        if skip_system and name.startswith(("sys_", "tmp_", "backup_", "test_")):
            print(f"⏭️  Skipping system/temporary table: {name}")
            continue
        print(f"🔹 [{i}/{total}] Processing table: {name}")
        try:
            doc = build_table_doc(t, sample_n)
            docs.append(doc)
        except Exception as e:
            print(f"⚠️ Error processing {name}: {e}")
    print(f"✅ Extracted {len(docs)} table docs successfully.")
    return docs

if __name__ == "__main__":
    docs = extract_all(5)
    print(f"Extracted {len(docs)} tables")
    with open("extracted_table_docs.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
