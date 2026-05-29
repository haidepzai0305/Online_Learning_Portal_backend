from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.utils.auth_middleware import jwt_required
from myproject.notification_service.app.models.notifications import Notification

@csrf_exempt
@jwt_required
def list_my_notifications_view(request):
    """
    Lấy danh sách thông báo của người dùng
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    notifications = Notification.objects.filter(user_id=request.user_id)
    data = [{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat()
    } for n in notifications]
    
    return JsonResponse({"notifications": data})

@csrf_exempt
@jwt_required
def mark_notification_read_view(request, notification_id):
    """
    Đánh dấu một thông báo là đã đọc
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        notification = Notification.objects.get(id=notification_id, user_id=request.user_id)
        notification.is_read = True
        notification.save()
        return JsonResponse({"message": "Notification marked as read"})
    except Notification.DoesNotExist:
        return JsonResponse({"error": "Notification not found"}, status=404)
