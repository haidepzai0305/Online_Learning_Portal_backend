import json
import pika
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
USER_REGISTERED_QUEUE = "user_registered_queue"
USER_AUTH_QUEUE = "user_auth_queue"

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f" [x] Consumed from {method.routing_key}: {data}")
        # Here you would add logic to sync users, update profiles, etc.
        # Example: if method.routing_key == USER_REGISTERED_QUEUE:
        #             create_local_user_profile(data)
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [!] Error processing message: {e}")

def main():
    print(f" [*] Connecting to RabbitMQ at {RABBITMQ_URL}...")
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Declare queues to ensure they exist
        channel.queue_declare(queue=USER_REGISTERED_QUEUE, durable=True)
        channel.queue_declare(queue=USER_AUTH_QUEUE, durable=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')

        channel.basic_consume(queue=USER_REGISTERED_QUEUE, on_message_callback=callback)
        channel.basic_consume(queue=USER_AUTH_QUEUE, on_message_callback=callback)

        channel.start_consuming()
    except Exception as e:
        print(f" [!] Connection failed: {e}")

if __name__ == '__main__':
    main()
