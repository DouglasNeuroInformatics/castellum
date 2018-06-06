import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import Address


class Subject(models.Model):
    GENDER = (
        ("f", _("female")),
        ("m", _("male")),
        ("*", _("diverse")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(_("first name"), max_length=64)
    last_name = models.CharField(_("last name"), max_length=64)

    gender = models.CharField(_("gender"), max_length=1, choices=GENDER, default="f")

    birthday = models.DateField(_("birthday"))

    address = models.ForeignKey(Address, blank=True, null=True, verbose_name=_("Address"),
                                on_delete=models.SET_NULL)
    email = models.EmailField(_("email"), max_length=128, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=32, blank=True)
    phone_number_alternative = models.CharField(_("phone number alternative"), max_length=32,
                                                blank=True)
