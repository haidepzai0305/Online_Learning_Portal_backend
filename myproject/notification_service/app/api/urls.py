from django.urls import path
from .views import list_my_notifications_view, mark_notification_read_view

urlpatterns = [
    path('', list_my_notifications_view, name='list-notifications'),
    path('<int:notification_id>/read/', mark_notification_read_view, name='mark-notification-read'),
]
