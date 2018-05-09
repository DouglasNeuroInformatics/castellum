from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    expiration_date = models.DateTimeField(_('Expiration date'), blank=True, null=True)

    @property
    def logout_timeout(self):
        return 15 * 60
