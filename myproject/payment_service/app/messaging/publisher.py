import pika
import json
import os

class PaymentPublisher:
    def __init__(self):
        self.url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            if not self.connection or self.connection.is_closed:
                params = pika.URLParameters(self.url)
                self.connection = pika.BlockingConnection(params)
                self.channel = self.connection.channel()
                self.channel.exchange_declare(exchange='unilearn_events', exchange_type='topic', durable=True)
        except Exception as e:
            print(f"DEBUG RabbitMQ Connection Error: {e}")
            raise e

    def publish_payment_success(self, transaction_id, user_id, course_id, amount):
        self.connect()
        message = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "course_id": course_id,
            "amount": float(amount),
            "status": "SUCCESS"
        }
        self.channel.basic_publish(
            exchange='unilearn_events',
            routing_key='payment.success',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent payment success for Course {course_id}")

    def publish_payment_failed(self, transaction_id, user_id, course_id, reason="Unknown"):
        self.connect()
        message = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "course_id": course_id,
            "status": "FAILED",
            "reason": reason
        }
        self.channel.basic_publish(
            exchange='unilearn_events',
            routing_key='payment.failed',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent payment failed for Course {course_id}")

publisher = PaymentPublisher()
