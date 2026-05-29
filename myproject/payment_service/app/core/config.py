import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
env_path = os.path.join(BASE_DIR, 'myproject', 'auth_service', 'app', 'core', '.env')
load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = "Online Learning Portal - Payment Service"
    DATABASE_NAME: str = "payment_db"
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

settings = Settings()
