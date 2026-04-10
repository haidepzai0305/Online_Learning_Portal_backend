import json

class RabbitMQPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._pika = None

    def _load_pika(self):
        if self._pika is not None:
            return True
        try:
            import pika as _pika_mod
            self._pika = _pika_mod
            return True
        except (ImportError, ModuleNotFoundError) as exc:
            print(f"[RabbitMQ] pika import failed ({exc}). Messaging disabled.")
            return False

    def connect(self):
        if not self._load_pika():
            return False

        from myproject.courses_service.app.core.config import settings
        try:
            params = self._pika.URLParameters(settings.RABBITMQ_URL)
            self.connection = self._pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=settings.COURSE_EVENTS_QUEUE, durable=True)
            return True
        except Exception as e:
            print(f"[RabbitMQ] Failed to connect ({settings.RABBITMQ_URL}): {e}")
            self.connection = None
            self.channel = None
            return False

    def publish_event(self, event_type: str, data: dict) -> None:
        if not self._load_pika():
            return

        if not self.connection or self.connection.is_closed:
            if not self.connect():
                return

        try:
            if self.channel is None:
                return

            event_data = {
                "event_type": event_type,
                "data": data
            }
            message = json.dumps(event_data)
            
            from myproject.courses_service.app.core.config import settings
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.COURSE_EVENTS_QUEUE,
                body=message,
                properties=self._pika.BasicProperties(delivery_mode=2),
            )
            print(f"[RabbitMQ] Sent event '{event_type}'")
        except Exception as e:
            print(f"[RabbitMQ] Failed to publish message: {e}")

    def close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass

publisher = RabbitMQPublisher()
