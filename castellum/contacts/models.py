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
from django.core import checks
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.pseudonyms.helpers import create_pseudonym
from castellum.pseudonyms.helpers import delete_pseudonym
from castellum.pseudonyms.helpers import get_subject
from castellum.utils.fields import DateField
from castellum.utils.fields import PhoneNumberField
from castellum.utils.models import TimeStampedModel

from .utils import phonetic


class Address(models.Model):
    country = models.CharField(_('Country'), max_length=64)
    city = models.CharField(_('City'), max_length=128)
    zip_code = models.CharField(_('Zip code'), max_length=5)
    street = models.CharField(_('Street'), max_length=128)
    house_number = models.CharField(_('House number'), max_length=5)
    additional_information = models.CharField(
        _('Additional information'), max_length=32, blank=True
    )

    def lines(self):
        line1 = ' '.join([self.street, self.house_number, self.additional_information]).strip()
        line2 = '{} {}'.format(self.zip_code, self.city)
        return line1, line2

    def __str__(self):
        return '{}, {}'.format(*self.lines())

    class Meta:
        ordering = (
            'country', 'city', 'zip_code', 'street', 'house_number', 'additional_information'
        )
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')


class ContactManager(models.Manager):
    def fuzzy_filter(self, search):
        parts = search.split()
        q = self.all_parts_match(parts) & (
            self.full_name_is_matched(parts) |
            self.email_is_matched(parts) |
            self.guardian_full_name_is_matched(parts) |
            self.guardian_email_is_matched(parts)
        )
        return self.filter(q)

    def match_name(self, part, prefix):
        lookup = prefix + '_name_phonetic__contains'
        q = models.Q()
        for code in phonetic(part, encode=False):
            q &= models.Q(**{lookup: ':{}:'.format(code)})
        return q

    def name_is_matched(self, parts, prefix):
        q = models.Q()
        for part in parts:
            if '@' not in part:
                q |= self.match_name(part, prefix)
        return q

    def full_name_is_matched(self, parts):
        return self.name_is_matched(parts, 'first') & self.name_is_matched(parts, 'last')

    def email_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q |= models.Q(email__iexact=part)
        return q

    def guardian_full_name_is_matched(self, parts):
        return (
            self.name_is_matched(parts, 'guardians__first') &
            self.name_is_matched(parts, 'guardians__last')
        )

    def guardian_email_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q |= models.Q(guardians__email__iexact=part)
        return q

    def all_parts_match(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q &= (
                    models.Q(email__iexact=part) |
                    models.Q(guardians__email__iexact=part)
                )
            else:
                q &= (
                    self.match_name(part, 'first') |
                    self.match_name(part, 'last') |
                    self.match_name(part, 'guardians__first') |
                    self.match_name(part, 'guardians__last')
                )
        return q


class Contact(TimeStampedModel):
    domain = settings.CASTELLUM_DOMAINS['contact']['key']

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

    pseudonym = models.CharField(max_length=64, unique=True, editable=False, default=None)

    first_name = models.CharField(_('First name'), max_length=64)
    first_name_phonetic = models.CharField(max_length=128, editable=False, default=None)
    last_name = models.CharField(_('Last name'), max_length=64)
    last_name_phonetic = models.CharField(max_length=128, editable=False, default=None)
    title = models.CharField(_('Title'), max_length=64, blank=True)

    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER, default="f")

    date_of_birth = DateField(_('Date of birth'), blank=True, null=True)

    address = models.ForeignKey(
        Address, blank=True, null=True, verbose_name=_('Address'), on_delete=models.SET_NULL
    )
    email = models.EmailField(_('Email'), max_length=128, blank=True)
    phone_number = PhoneNumberField(_('Phone number'), max_length=32, blank=True)
    phone_number_alternative = PhoneNumberField(
        _('Phone number alternative'), max_length=32, blank=True
    )

    preferred_contact_method = models.CharField(
        _('Preferred contact method'), max_length=16, blank=True, choices=CONTACT_METHODS
    )

    guardians = models.ManyToManyField(
        'contacts.Contact', verbose_name=_('Guardians'), related_name='guardian_of', blank=True
    )

    objects = ContactManager()

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return self.full_name

    @cached_property
    def subject(self):
        return get_subject(self.domain, self.pseudonym)

    @property
    def is_complete(self):
        return self.date_of_birth and any([
            self.address, self.phone_number, self.email, self.has_guardian
        ])

    @property
    def full_name(self):
        return " ".join(filter(None, [self.title, self.first_name, self.last_name]))

    @property
    def age(self):
        return relativedelta(date.today(), self.date_of_birth).years

    @property
    def has_guardian(self):
        return self.id and self.guardians.exists()

    def save(self, *args, **kwargs):
        if not self.pseudonym:
            self.pseudonym = create_pseudonym(Contact.domain)

        self.first_name_phonetic = phonetic(self.first_name)
        self.last_name_phonetic = phonetic(self.last_name)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.pseudonym:
            delete_pseudonym(Contact.domain, self.pseudonym)
        if self.address:
            self.address.delete()
        return super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('subjects:detail', args=[self.subject.pk])


@checks.register(checks.Tags.security, deploy=True)
def check_domain_unchanged(app_configs, **kwargs):
    errors = []
    domain = settings.CASTELLUM_DOMAINS['contact']
    if domain and domain['key'] == 'CHANGEME':
        errors.append(checks.Error(
            'You have not changed the contact domain key.',
            id='castellum.contacts.E002',
        ))
    return errors
