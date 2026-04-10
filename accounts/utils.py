from .models import Notification, User


def create_notification(*, user: User, title: str, message: str, link: str = "") -> Notification:
    return Notification.objects.create(user=user, title=title, message=message, link=link)

