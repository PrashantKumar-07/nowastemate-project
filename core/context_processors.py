from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        latest_notifications = request.user.notifications.order_by('-created_at')[:5]
        return {
            'unread_notification_count': unread_count,
            'latest_notifications': latest_notifications
        }
    return {}