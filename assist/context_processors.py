# assist/context_processors.py
def unread_notifications(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(read=False).count()
    return {"unread_count": unread_count}
