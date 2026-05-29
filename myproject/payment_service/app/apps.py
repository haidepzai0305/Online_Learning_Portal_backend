from django.apps import AppConfig

class PaymentServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.payment_service.app'
    label = 'payment_service'
