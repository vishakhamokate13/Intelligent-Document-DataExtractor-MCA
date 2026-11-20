
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "intelligent-document-secret-key"

    DATABASE = os.path.join(
        BASE_DIR, "database", "document_extractor.db"
    )

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    ALLOWED_EXTENSIONS = {
        "pdf", "png", "jpg", "jpeg"
    }
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}