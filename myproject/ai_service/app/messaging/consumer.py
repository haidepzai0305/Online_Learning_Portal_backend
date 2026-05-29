import json
import pika
import os
import django
from dotenv import load_dotenv

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.ai_service.app.services.rag_service import RAGService

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event_type = data.get("event_type")
        payload = data.get("payload", {})
        
        print(f" [x] AI Service received {event_type}")

        if event_type == "material_uploaded":
            course_id = payload.get("course_id")
            content = payload.get("content") # Assume text content for now
            if course_id and content:
                print(f"Indexing new material for Course {course_id}...")
                RAGService.index_document(str(course_id), content)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] AI processing error: {e}")

def main():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(exchange='portal_events', exchange_type='fanout', durable=True)
    
    result = channel.queue_declare(queue='ai_service_queue', durable=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='portal_events', queue=queue_name)

    print(' [*] AI Service waiting for events. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    main()
