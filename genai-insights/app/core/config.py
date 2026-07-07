from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Project root (genai-insights/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DB_URL = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

settings = Settings()
