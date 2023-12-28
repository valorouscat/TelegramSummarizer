from dotenv import load_dotenv
from pathlib import Path
import os


env_path = Path(".") / ".env"

load_dotenv(dotenv_path=env_path)

# env vars
class Config:
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    API_HOST = os.getenv("API_HOST")
    TABLE_NAME = os.getenv("TABLE_NAME")


