from core.models import Notification
from django.db.models import Q

def notification_count(request):
    if not request.user.is_authenticated or request.user.role == 'admin':
        return {}

    count = Notification.objects.filter(
        Q(recipient_role=request.user.role) | Q(recipient_role='all')
    ).count()

    return {'notification_count': count}