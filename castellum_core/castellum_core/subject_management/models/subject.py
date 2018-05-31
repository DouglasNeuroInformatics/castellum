import uuid

from django.db import models

from . import Address


class Subject(models.Model):
    GENDER = (
        ("f", "female"),
        ("m", "male"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    gender = models.CharField(max_length=1, choices=GENDER, default="f")

    birthday = models.DateField()

    address = models.ForeignKey(Address, blank=True, null=True, on_delete=models.SET_NULL)
    email = models.EmailField(max_length=128, blank=True, default="")
    phone_number = models.CharField(max_length=32, blank=True, default="")
    phone_number_alternative = models.CharField(max_length=32, blank=True, default="")
