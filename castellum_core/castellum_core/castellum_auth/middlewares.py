from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


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
