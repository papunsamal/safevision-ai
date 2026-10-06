import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    AI_MODE = os.getenv("AI_MODE", "DEMO")
    MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "models", "ppe_model.pt"))
    FIRE_SMOKE_MODEL_PATH = os.getenv("FIRE_SMOKE_MODEL_PATH", os.path.join(BASE_DIR, "models", "fire_smoke_model.pt"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
    EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence", "alerts")
    CONFIGS_DIR = os.path.join(BASE_DIR, "configs")

    # MySQL 8.0
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "safevision")


settings = Settings()