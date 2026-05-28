from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.timezone import now
from .models import UserActivity


@receiver(user_logged_in)
def login_handler(sender, request, user, **kwargs):

    activity, created = UserActivity.objects.get_or_create(user=user)

    activity.session_start = now()   # ВАЖНО
    activity.save()


@receiver(user_logged_out)
def logout_handler(sender, request, user, **kwargs):

    if not user or not user.is_authenticated:
        return

    activity, created = UserActivity.objects.get_or_create(user=user)

    activity.last_seen = now()
    activity.save()