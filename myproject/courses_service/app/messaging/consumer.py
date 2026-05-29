import json
import pika
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
USER_REGISTERED_QUEUE = "user_registered_queue"
USER_AUTH_QUEUE = "user_auth_queue"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        routing_key = method.routing_key
        
        print(f" [x] Courses Service received {routing_key}")

        if routing_key == "payment.success":
            user_id = data.get("user_id")
            course_id = data.get("course_id")
            print(f"Enrolling student {user_id} in course {course_id} after successful payment.")
            from myproject.courses_service.app.services.course_service import CourseService
            CourseService.enroll_student(course_id, user_id)
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Error processing message: {e}")

def main():
    print(f" [*] Connecting to RabbitMQ at {RABBITMQ_URL}...")
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Declare the exchange as topic
        channel.exchange_declare(exchange='unilearn_events', exchange_type='topic', durable=True)
        
        # Create a temporary queue for this service
        result = channel.queue_declare(queue='courses_service_payment_queue', durable=True)
        queue_name = result.method.queue
        
        # Bind for various events
        channel.queue_bind(exchange='unilearn_events', queue=queue_name, routing_key='payment.success')
        channel.queue_bind(exchange='unilearn_events', queue=queue_name, routing_key='user.registered')

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        channel.start_consuming()
    except Exception as e:
        print(f" [!] Connection failed: {e}")

if __name__ == '__main__':
    main()
