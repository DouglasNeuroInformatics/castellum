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
from django.core.validators import MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.pseudonyms.helpers import create_pseudonym
from castellum.pseudonyms.models import SubjectData
from castellum.utils.fields import DateField
from castellum.utils.fields import DateTimeField
from castellum.utils.fields import PhoneNumberField

from . import Address
from .timeslot import TimeSlot
from ..utils import phonetic


class ContactManager(models.Manager):
    def fuzzy_filter(self, first_name, last_name, date_of_birth):
        q = models.Q(date_of_birth=date_of_birth)
        for code in phonetic(first_name, encode=False):
            q &= models.Q(first_name_phonetic__contains=':{}:'.format(code))
        for code in phonetic(last_name, encode=False):
            q &= models.Q(last_name_phonetic__contains=':{}:'.format(code))
        return self.filter(q)


class Contact(SubjectData):
    domain = settings.DOMAINS['contact']

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
    first_name_phonetic = models.CharField(max_length=128, editable=False)
    last_name = models.CharField(_("last name"), max_length=64)
    last_name_phonetic = models.CharField(max_length=128, editable=False)
    title = models.CharField(_("title"), max_length=64, blank=True)

    gender = models.CharField(_("gender"), max_length=1, choices=GENDER, default="f")

    date_of_birth = DateField(_("date of birth"))

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

    privacy_level = models.PositiveIntegerField(
        _("privacy level"), validators=[MaxValueValidator(2)])

    objects = ContactManager()

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    @property
    def full_name(self):
        return " ".join(filter(None, [self.title, self.first_name, self.last_name]))

    @property
    def age(self):
        return relativedelta(date.today(), self.date_of_birth).years

    @property
    def is_available(self):
        now = timezone.localtime()
        if self.not_available_until and self.not_available_until > now:
            return False
        days = [
            self.availability_monday,
            self.availability_tuesday,
            self.availability_wednesday,
            self.availability_thursday,
            self.availability_friday,
        ]
        if now.weekday() >= len(days):
            return False
        hours = days[now.weekday()]
        return hours.filter(hour=now.hour).exists()

    def get_availability_monday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_monday.all())

    def get_availability_tuesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_tuesday.all())

    def get_availability_wednesday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_wednesday.all())

    def get_availability_thursday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_thursday.all())

    def get_availability_friday_display(self):
        return ', '.join(str(ts.hour) for ts in self.availability_friday.all())

    def save(self, *args, **kwargs):
        if not self.pseudonym:
            self.pseudonym = create_pseudonym(Contact.domain)

        self.first_name_phonetic = phonetic(self.first_name)
        self.last_name_phonetic = phonetic(self.last_name)

        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('contacts:detail', args=[self.pseudonym])
