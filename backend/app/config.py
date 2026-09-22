import os
from pathlib import Path

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DOCUMENTS_DIR = BASE_DIR / "documents"

CHROMA_DIR = BASE_DIR / "backend" / "data" / "chroma_db"

GROQ_API_KEY = os.getenv("GROQ_APIKEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Create backend/.env and add GROQ_API_KEY."
    )