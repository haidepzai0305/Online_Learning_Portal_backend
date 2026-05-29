import pika
import json
from myproject.auth_service.app.core.config import settings

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            # Standardize on a topic exchange
            self.channel.exchange_declare(exchange='unilearn_events', exchange_type='topic', durable=True)
            return True
        except Exception as e:
            print(f"Failed to connect to RabbitMQ at {settings.RABBITMQ_URL}: {e}")
            self.connection = None
            self.channel = None
            return False

    def publish_user_registered(self, user_data):
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                print("Skipping message publishing because RabbitMQ is unavailable.")
                return

        try:
            if self.channel is None:
                print("RabbitMQ channel is not initialized. Cannot publish message.")
                return

            # Standardized event structure
            message = json.dumps(user_data)
            
            self.channel.basic_publish(
                exchange='unilearn_events',
                routing_key='user.registered',
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            print(f" [x] Sent event 'user.registered' to unilearn_events exchange")
        except Exception as e:
            print(f"Failed to publish message: {e}")

    def close(self):
        if self.connection:
            self.connection.close()

# Singleton instance
publisher = RabbitMQPublisher()
