# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # read .env if present

BASE_DIR = Path(__file__).resolve().parent.parent

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3307))
DB_NAME = os.getenv("DB_NAME", "demo_db")
DB_USER = os.getenv("DB_USER", "demo_user")
DB_PASS = os.getenv("DB_PASS", "demo_pass")
DB_URI = os.getenv("DB_URI") or f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

CHROMA_DIR = os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_store"))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_BATCH = int(os.getenv("EMBED_BATCH", "32"))

# OpenAI-like client config (we'll import LLM_API_1 if the user provided it)
# You may alternatively set OPENAI_API_KEY and OPENAI_BASE_URL
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
