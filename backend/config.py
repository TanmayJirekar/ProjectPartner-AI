import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "tanmay2305"),
    "database": os.getenv("DB_NAME", "projectpartner_ai"),
}

SECRET_KEY = os.getenv("SECRET_KEY", "projectpartner-ai-secret-key-2026")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

UPLOAD_FOLDER = BASE_DIR / "project_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "ppt", "pptx", "mp4", "doc", "docx"}
