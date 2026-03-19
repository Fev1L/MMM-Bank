from .models import InboxMessage

def unread_messages(request):
    if request.user.is_authenticated:
        count = InboxMessage.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()
    else:
        count = 0

    return {
        'unread_count': count
    }