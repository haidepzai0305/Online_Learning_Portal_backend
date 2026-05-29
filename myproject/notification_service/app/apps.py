from django.apps import AppConfig

class NotificationAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.notification_service.app'
    label = 'notification_service_app'
