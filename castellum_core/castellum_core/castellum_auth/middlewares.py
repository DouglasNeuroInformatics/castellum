from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'


class UserExpirationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            error = None
            if not request.user.expiration_date:
                error = _('Your account is not activated.')
            elif request.user.expiration_date < timezone.now():
                error = _('Your account is expired.')

            if error is not None:
                logout(request)
                messages.add_message(request, messages.ERROR, error)

        return self.get_response(request)


def get_last_active(request):
    s = request.session['_last_active']
    return timezone.datetime.strptime(s, DATETIME_FORMAT)


def set_last_active(request):
    now = timezone.now()
    request.session['_last_active'] = now.strftime(DATETIME_FORMAT)


class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            logout_timeout = 15 * 60
            idle_time = timezone.now() - get_last_active(request)
            if idle_time.total_seconds() > logout_timeout:
                logout(request)
            elif idle_time.total_seconds() > logout_timeout / 10:
                set_last_active(request)

        return self.get_response(request)


@receiver(user_logged_in)
def set_last_active_on_login(sender, user, request, **kwargs):
    set_last_active(request)
