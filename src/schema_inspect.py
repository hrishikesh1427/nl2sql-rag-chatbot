from sqlalchemy import create_engine, inspect, text
import json
import pandas as pd
import hashlib
from datetime import datetime
from src.config import DB_URI

engine = create_engine(DB_URI, pool_pre_ping=True, future=True)
inspector = inspect(engine)

def compute_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def sample_rows(table: str, n: int = 5):
    q = text(f"SELECT * FROM `{table}` LIMIT :n")
    with engine.connect() as conn:
        try:
            df = pd.read_sql(q, conn, params={"n": n})
            return df.fillna("").astype(str).to_dict(orient="records")
        except Exception:
            return []

def build_table_doc(table: str, sample_n: int = 5):
    cols = inspector.get_columns(table)
    fks = inspector.get_foreign_keys(table)
    idxs = inspector.get_indexes(table)
    samples = sample_rows(table, sample_n)

    parts = [f"Table: {table}", "Columns:"]
    for c in cols:
        parts.append(
            f"- {c['name']}: {c['type']} "
            f"nullable={c['nullable']} "
            f"default={c.get('default')}"
        )
    if fks:
        parts.append("Foreign Keys:")
        for fk in fks:
            parts.append(f"- {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    if idxs:
        parts.append("Indexes:")
        for idx in idxs:
            parts.append(f"- {idx['name']} unique={idx['unique']} cols={idx['column_names']}")

    if samples:
        parts.append("Sample rows:")
        for r in samples:
            parts.append(json.dumps(r, default=str))

    full_text = "\n".join(parts)
    return {
        "table": table,
        "text": full_text,
        "schema_hash": compute_hash(full_text),
        "created_at": datetime.utcnow().isoformat(),
        "columns": cols,
        "fks": fks,
        "samples": samples
    }

def extract_all(sample_n: int = 5):
    tables = inspector.get_table_names()
    docs = []
    for i, table in enumerate(tables, start=1):
        print(f"🔹 [{i}/{len(tables)}] Processing {table}")
        docs.append(build_table_doc(table, sample_n))
    print(f"✅ Extracted {len(docs)} tables.")
    return docs

if __name__ == "__main__":
    docs = extract_all(5)
    with open("extracted_table_docs.json", "w") as f:
        json.dump(docs, f, indent=2)
