# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import cologne_phonetics
from dateutil.relativedelta import relativedelta

from castellum.pseudonyms.helpers import create_pseudonym
from castellum.pseudonyms.models import SubjectData
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField
from castellum.utils.fields import PhoneNumberField

from . import Address


def phonetic(s, encode=True):
    codes = [code for __, code in cologne_phonetics.encode(s)]
    if encode:
        return ':' + ':'.join(codes) + ':'
    else:
        return codes


class TimeSlot(models.Model):
    hour = models.PositiveSmallIntegerField(_('hour'))

    class Meta:
        ordering = ['hour']

    def __str__(self):
        return str(self.hour)


class ContactManager(models.Manager):
    def fuzzy_filter(self, first_name, last_name, birthday):
        q = models.Q(birthday=birthday)
        for code in phonetic(first_name, encode=False):
            q &= models.Q(first_name_phonetic__contains=':{}:'.format(code))
        for code in phonetic(last_name, encode=False):
            q &= models.Q(last_name_phonetic__contains=':{}:'.format(code))
        return self.filter(q)


class Contact(SubjectData):
    GENDER = (
        ("f", _("female")),
        ("m", _("male")),
        ("*", _("diverse")),
    )
    CONTACT_METHODS = (
        ("phone", _("phone")),
        ("email", _("email")),
        ("postal", _("postal")),
    )

    first_name = models.CharField(_("first name"), max_length=64)
    first_name_phonetic = models.CharField(max_length=16, editable=False)
    last_name = models.CharField(_("last name"), max_length=64)
    last_name_phonetic = models.CharField(max_length=16, editable=False)
    title = models.CharField(_("title"), max_length=64, blank=True)

    gender = models.CharField(_("gender"), max_length=1, choices=GENDER, default="f")

    birthday = DateField(_("birthday"))

    address = models.ForeignKey(Address, blank=True, null=True, verbose_name=_("address"),
                                on_delete=models.SET_NULL)
    email = models.EmailField(_("email"), max_length=128, blank=True)
    phone_number = PhoneNumberField(_("phone number"), max_length=32, blank=True)
    phone_number_alternative = PhoneNumberField(_("phone number alternative"), max_length=32,
                                                blank=True)

    preferred_contact_method = models.CharField(
        _("preferred contact method"), max_length=16, blank=True, choices=CONTACT_METHODS)

    availability_monday = models.ManyToManyField(
        TimeSlot, verbose_name=_("monday"), blank=True, related_name='+')
    availability_tuesday = models.ManyToManyField(
        TimeSlot, verbose_name=_("tuesday"), blank=True, related_name='+')
    availability_wednesday = models.ManyToManyField(
        TimeSlot, verbose_name=_("wednesday"), blank=True, related_name='+')
    availability_thursday = models.ManyToManyField(
        TimeSlot, verbose_name=_("thursday"), blank=True, related_name='+')
    availability_friday = models.ManyToManyField(
        TimeSlot, verbose_name=_("friday"), blank=True, related_name='+')

    not_available_until = DateTimeField(_("not available until"), blank=True, null=True)

    objects = ContactManager()

    @property
    def age(self):
        if self.birthday:
            delta = relativedelta(date.today(), self.birthday)
            return delta.years
        return None

    @property
    def available(self):
        now = timezone.localtime()
        if self.not_available_until and self.not_available_until >= now:
            return False
        days = [
            self.availability_monday,
            self.availability_tuesday,
            self.availability_wednesday,
            self.availability_thursday,
            self.availability_friday,
        ]
        if now.weekday() < len(days):
            hours = days[now.weekday()]
            return hours.filter(hour=now.hour).exists()
        return False

    def save(self, *args, **kwargs):
        if not self.pseudonym:
            self.pseudonym = create_pseudonym(settings.DOMAINS['contact'])

        self.first_name_phonetic = phonetic(self.first_name)
        self.last_name_phonetic = phonetic(self.last_name)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('contacts:detail', args=[self.pseudonym])

    def full_name(self):
        name = self.first_name + ' ' + self.last_name
        if self.title:
            name = self.title + ' ' + name
        return name
