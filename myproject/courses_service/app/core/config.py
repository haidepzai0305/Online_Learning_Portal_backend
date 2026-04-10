import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Online Learning Portal - Courses Service"
    
    # RabbitMQ
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    COURSE_EVENTS_QUEUE = "course_events_queue"

settings = Settings()
