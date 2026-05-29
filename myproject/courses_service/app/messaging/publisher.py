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
            
            # Using a Topic exchange for flexible system-wide events
            self.channel.exchange_declare(exchange='unilearn_events', exchange_type='topic', durable=True)
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
                "payload": data 
            }
            message = json.dumps(event_data)
            
            # Convert underscore event name to dotted routing key
            routing_key = event_type.replace('_', '.')
            
            self.channel.basic_publish(
                exchange='unilearn_events',
                routing_key=routing_key,
                body=message,
                properties=self._pika.BasicProperties(delivery_mode=2),
            )
            print(f"[RabbitMQ] Sent event '{event_type}' to unilearn_events exchange with key '{routing_key}'")
        except Exception as e:
            print(f"[RabbitMQ] Failed to publish message: {e}")

    def close(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass

publisher = RabbitMQPublisher()
