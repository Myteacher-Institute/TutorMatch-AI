from .models import ChatMessage


def chat_badges(request):
    if not request.user.is_authenticated:
        return {"chat_unread_count": 0}

    unread_messages = ChatMessage.objects.filter(is_read=False)

    if request.user.is_staff:
        return {"chat_unread_count": unread_messages.count()}

    unread_messages = unread_messages.exclude(sender=request.user)

    if hasattr(request.user, "profile"):
        if request.user.profile.role == request.user.profile.ROLE_STUDENT:
            unread_messages = unread_messages.filter(session__student=request.user)
        elif request.user.profile.role == request.user.profile.ROLE_TUTOR:
            unread_messages = unread_messages.filter(session__tutor=request.user)
        else:
            unread_messages = unread_messages.none()
    else:
        unread_messages = unread_messages.none()

    return {"chat_unread_count": unread_messages.count()}
