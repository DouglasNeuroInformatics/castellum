# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.castellum_auth.models import User
from castellum.subjects.models import Subject
from castellum.utils import uuid_str


class Domain(models.Model):
    key = models.CharField(max_length=64, default=uuid_str, unique=True, editable=False)
    name = models.CharField(max_length=64, blank=True)
    bits = models.PositiveIntegerField(default=40)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    context = GenericForeignKey()

    managers = models.ManyToManyField(
        User,
        verbose_name=_('Users who can access this pseudonym list'),
        related_name='general_domains',
        blank=True,
    )
    exportable_attributes = models.ManyToManyField(
        'recruitment.Attribute',
        verbose_name=_('Exportable recruitment attributes'),
        related_name='+',
        blank=True,
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name or self.key


class Pseudonym(models.Model):
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, blank=True, null=True
    )
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    pseudonym = models.CharField(max_length=64, default=None)

    class Meta:
        unique_together = [
            ['domain', 'pseudonym'],
            ['domain', 'subject'],
        ]

    def __str__(self):
        return self.pseudonym

    def save(self, *args, **kwargs):
        if not self.pseudonym:
            self.pseudonym = settings.CASTELLUM_PSEUDONYM_GENERATE(self.domain.bits)
        super().save(*args, **kwargs)


def generate_private_key():
    private_key = ed25519.Ed25519PrivateKey.generate()
    return private_key.private_bytes_raw()


class KeyPair(models.Model):
    pseudonym = models.OneToOneField(Pseudonym, on_delete=models.CASCADE)
    private_key = models.BinaryField(default=generate_private_key)

    def get_private_key(self):
        return ed25519.Ed25519PrivateKey.from_private_bytes(self.private_key)

    def get_public_key(self):
        return self.get_private_key().public_key()

    def get_ssh_private_key(self):
        return self.get_private_key().private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode('utf-8')

    def get_ssh_public_key(self):
        return self.get_public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH,
        ).decode('utf-8')
