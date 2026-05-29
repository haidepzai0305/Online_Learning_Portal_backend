from myproject.notification_service.app.models.notifications import Notification

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message):
        return Notification.objects.create(
            user_id=user_id,
            title=title,
            message=message
        )

    @staticmethod
    def get_user_notifications(user_id):
        return Notification.objects.filter(user_id=user_id)

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.objects.get(pk=notification_id, user_id=user_id)
        notification.is_read = True
        notification.save()
        return notification
