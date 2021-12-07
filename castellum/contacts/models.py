# (c) 2018-2021
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

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from castellum.subjects.models import Subject
from castellum.utils.fields import DateField
from castellum.utils.fields import PhoneNumberField
from castellum.utils.models import TimeStampedModel

from .utils import is_phone_number
from .utils import phonetic


class ContactQuerySet(models.QuerySet):
    def fuzzy_filter(self, search):
        parts = search.split()
        q = self.all_parts_match(parts) & (
            self.full_name_is_matched(parts) |
            self.phone_number_is_matched(parts) |
            self.email_is_matched(parts) |
            self.legal_representative_full_name_is_matched(parts) |
            self.legal_representative_phone_number_is_matched(parts) |
            self.legal_representative_email_is_matched(parts)
        )
        return self.filter(q).distinct()

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

    def phone_number_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' not in part and is_phone_number(part):
                q |= models.Q(phone_number=part)
                q |= models.Q(phone_number_alternative=part)
        return q

    def email_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q |= models.Q(email__iexact=part)
        return q

    def legal_representative_full_name_is_matched(self, parts):
        return (
            self.name_is_matched(parts, 'legal_representatives__first') &
            self.name_is_matched(parts, 'legal_representatives__last')
        )

    def legal_representative_phone_number_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' not in part and is_phone_number(part):
                q |= models.Q(legal_representatives__phone_number=part)
                q |= models.Q(legal_representatives__phone_number_alternative=part)
        return q

    def legal_representative_email_is_matched(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q |= models.Q(legal_representatives__email__iexact=part)
        return q

    def all_parts_match(self, parts):
        q = models.Q()
        for part in parts:
            if '@' in part:
                q &= (
                    models.Q(email__iexact=part) |
                    models.Q(legal_representatives__email__iexact=part)
                )
            elif is_phone_number(part):
                q &= (
                    models.Q(phone_number=part) |
                    models.Q(phone_number_alternative=part) |
                    models.Q(legal_representatives__phone_number=part) |
                    models.Q(legal_representatives__phone_number_alternative=part)
                )
            else:
                q &= (
                    self.match_name(part, 'first') |
                    self.match_name(part, 'last') |
                    self.match_name(part, 'legal_representatives__first') |
                    self.match_name(part, 'legal_representatives__last')
                )
        return q


class BaseContact(TimeStampedModel):
    GENDER = [
        ("f", _("female")),
        ("m", _("male")),
        ("*", _("diverse")),
    ]

    first_name = models.CharField(_('First name'), max_length=64)
    last_name = models.CharField(_('Last name'), max_length=64)
    title = models.CharField(_('Title'), max_length=64, blank=True)

    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER, blank=True)
    date_of_birth = DateField(_('Date of birth'), blank=True, null=True)
    phone_number = PhoneNumberField(_('Phone number'), max_length=32, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return " ".join(filter(None, [self.title, self.first_name, self.last_name]))

    @property
    def short_name(self):
        # a bit simplistic, but should be sufficient
        return '{}. {}'.format(self.first_name[0], self.last_name)


class Contact(BaseContact):
    CONTACT_METHODS = [
        ("phone", _("phone")),
        ("email", _("email")),
        ("postal", _("postal")),
    ]

    subject_uuid = models.UUIDField(unique=True, editable=False, default=None)

    first_name_phonetic = models.CharField(max_length=128, editable=False, default=None)
    last_name_phonetic = models.CharField(max_length=128, editable=False, default=None)

    email = models.EmailField(_('Email'), max_length=128, blank=True)
    phone_number_alternative = PhoneNumberField(
        _('Phone number alternative'), max_length=32, blank=True
    )

    preferred_contact_method = models.CharField(
        _('Preferred contact method'), max_length=16, blank=True, choices=CONTACT_METHODS
    )

    legal_representatives = models.ManyToManyField(
        'contacts.Contact',
        verbose_name=_('Legal representatives'),
        related_name='legal_representative_of',
        blank=True,
    )

    objects = ContactQuerySet.as_manager()

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('Contact data')
        verbose_name_plural = _('Contact data')

    def get_address(self):
        try:
            return self.address
        except Address.DoesNotExist:
            return None

    @cached_property
    def subject(self):
        subject = Subject.objects.get(uuid=self.subject_uuid)
        subject.__dict__['contact'] = self
        return subject

    @property
    def is_complete(self):
        return (
            (self.is_legal_representative or self.date_of_birth)
            and self.is_reachable
            and self.gender
        )

    @property
    def is_reachable(self):
        return any([
            self.get_address(),
            self.phone_number,
            self.email,
            [c for c in self.legal_representatives.all() if not c.subject.blocked],
        ])

    @cached_property
    def is_legal_representative(self):
        return self.id and self.legal_representative_of.exists()

    @cached_property
    def has_legal_representative(self):
        return self.id and self.legal_representatives.exists()

    @cached_property
    def own_or_legal_representative_emails(self):
        if self.email:
            return [self.email]
        else:
            return [
                c.email
                for c in self.legal_representatives.exclude(email='')
                if not c.subject.blocked
            ]

    @cached_property
    def email_recipients_string(self):
        if len(self.own_or_legal_representative_emails) > 1:
            return ', '.join(
                c.full_name
                for c in self.legal_representatives.exclude(email='')
                if not c.subject.blocked
            )

    def save(self, *args, **kwargs):
        if not self.subject_uuid:
            subject = Subject.objects.create(attributes={})
            self.subject_uuid = subject.uuid

        self.first_name_phonetic = phonetic(self.first_name)
        self.last_name_phonetic = phonetic(self.last_name)

        # updates Subject.updated_at
        self.subject.save()

        return super().save(*args, **kwargs)


class Address(models.Model):
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE)
    country = models.CharField(_('Country'), max_length=64)
    city = models.CharField(_('City'), max_length=128)
    zip_code = models.CharField(_('Zip code'), max_length=5)
    street = models.CharField(_('Street'), max_length=128)
    house_number = models.CharField(_('House number'), max_length=16)
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
        ordering = [
            'country', 'city', 'zip_code', 'street', 'house_number', 'additional_information'
        ]
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def save(self, *args, **kwargs):
        # updates Subject.updated_at
        self.contact.subject.save()
        return super().save(*args, **kwargs)


class Street(models.Model):
    name = models.CharField(_('Name'), max_length=64)

    def __str__(self):
        return self.name


class ContactCreationRequest(BaseContact):
    subject_id = models.PositiveIntegerField(unique=True, editable=False, default=None)
    email = models.EmailField(_('Email'), max_length=128)
    message = models.TextField(_('Message'), blank=True)

    def convert_to_real_contact(self):
        return Contact.objects.create(
            first_name=self.first_name,
            last_name=self.last_name,
            title=self.title,
            gender=self.gender,
            date_of_birth=self.date_of_birth,
            email=self.email,
        )
