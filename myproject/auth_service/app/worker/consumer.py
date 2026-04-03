import pika
import json
import sys
import os

# Để import được từ project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from myproject.auth_service.app.core.config import settings

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f" [v] Received event: {data}")
    
    user_email = data.get("email")
    username = data.get("username")
    
    # GIẢ LẬP: Gửi Email chào mừng
    print(f" >>> Sending welcome email to {username} ({user_email})...")
    print(" >>> Email sent successfully!")
    
    # Xác nhận đã xử lý xong tin nhắn
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    params = pika.URLParameters(settings.RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=settings.USER_REGISTERED_QUEUE, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.USER_REGISTERED_QUEUE, on_message_callback=callback)

    channel.start_consuming()

if __name__ == '__main__':
    try:
        start_worker()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
