import os

from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL", "sqlite:///storage.db")
# Some managed PostgreSQL services still return the old postgres:// scheme.
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-key-change-me")
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "16"))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()
    STORAGE_ROOT = os.getenv("STORAGE_ROOT", "instance/uploads")
    S3_BUCKET = os.getenv("S3_BUCKET", "")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL") or None

    ALLOWED_EXTENSIONS = {
        "csv",
        "doc",
        "docx",
        "gif",
        "jpeg",
        "jpg",
        "pdf",
        "png",
        "ppt",
        "pptx",
        "txt",
        "webp",
        "xls",
        "xlsx",
        "zip",
    }
