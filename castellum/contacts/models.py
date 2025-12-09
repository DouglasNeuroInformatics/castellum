# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from castellum.subjects.models import Subject
from castellum.utils.fields import DateField
from castellum.utils.fields import PhoneNumberField
from castellum.utils.models import TimeStampedModel
from castellum.utils.models import q_all
from castellum.utils.models import q_any

from .utils import is_phone_number
from .utils import phonetic


class PotentialDuplicateError(Exception):
    def __init__(self, duplicates):
        self.duplicates = duplicates


class ContactQuerySet(models.QuerySet):
    def q_match_name(self, name, prefix):
        lookup = f'{prefix}_name_phonetic__contains'
        return q_all([
            models.Q(**{lookup: f':{code}:'})
            for code in phonetic(name, encode=False)

        ])

    def q_name_is_matched(self, names, prefix):
        return q_any([self.q_match_name(name, prefix) for name in names])

    def q_sub_name(self, name, prefix):
        return models.Q(**{f'{prefix}_name': name}) | q_any([
            models.Q(**{f'{prefix}_name': sub})
            for sub in name.split()
        ])

    def q_fuzzy_date_of_birth(self, date):
        return (
            models.Q(date_of_birth__year=date.year, date_of_birth__month=date.month)
            | models.Q(date_of_birth__year=date.year, date_of_birth__day=date.day)
            | models.Q(date_of_birth__month=date.month, date_of_birth__day=date.day)
        )

    def fuzzy_find(
        self,
        first_name,
        last_name,
        date_of_birth=None,
        emails=[],
        phone_numbers=[],
        legal_representative_of=[],
    ):
        """Heuristics for import scripts.

        -   If an exact match can be found, return the contact instance.
            The import script can then update it.
        -   If no potential matches can be found, return None.
            The import script can then continue and create a new subject.
        -   If potential matches can be found, raise PotentialDuplicateError.
            The import script should then notify a user:
            -   If the entry turns out to be new, the user should
                create a new subject with matching first name,
                last name, and date of birth. The script will then find and
                update this subject on the next run.
            -   If the entry turns out to be a duplicate, the user
                should update either the entry in the import data or in
                Castellum so that first_name, last_name, and date of
                birth match. Again, the entry will be found and updated
                on the next run.
        """

        # these properties are likey to be shared in a family,
        # but unlikely to be shared beyond that
        q_family = q_any(
            [models.Q(email__iexact=email) for email in emails]
            + [models.Q(phone_number=n) for n in phone_numbers]
            + [models.Q(phone_number_alternative=n) for n in phone_numbers]
            + [models.Q(legal_representative_of=c) for c in legal_representative_of]
        )

        if emails or phone_numbers or legal_representative_of or date_of_birth:
            q_certain = self.q_sub_name(first_name, 'first')

            if date_of_birth:
                q_certain &= (
                    self.q_sub_name(last_name, 'last')
                    & models.Q(date_of_birth=date_of_birth)
                ) | q_family
                q_certain &= (
                    models.Q(date_of_birth=None)
                    | self.q_fuzzy_date_of_birth(date_of_birth)
                )
            else:
                q_certain &= q_family

            certain = self.filter(q_certain).first()
            if certain:
                return certain

        # If we can compare date_of_birth, it and one of the others must match.
        # Otherwise, first name and one of the others must match.
        q_uncertain = self.q_name_is_matched(first_name.split(), 'first')
        q_uncertain &= self.q_name_is_matched(last_name.split(), 'last') | q_family
        if date_of_birth:
            q_uncertain &= models.Q(date_of_birth=None)
            q_uncertain |= self.q_fuzzy_date_of_birth(date_of_birth) & (
                self.q_name_is_matched(first_name.split(), 'first')
                | self.q_name_is_matched(last_name.split(), 'last')
                | q_family
            )
        q_uncertain &= (
            self.q_sub_name(first_name, 'first')
            | self.q_sub_name(last_name, 'last')
            | q_family
        )

        uncertain = self.filter(q_uncertain).distinct()
        if uncertain:
            raise PotentialDuplicateError(uncertain)

    def search(self, query):
        # It is common that parents contact us about their children,
        # so it is useful to be able to find children by their parent's
        # contact data.

        emails = []
        phone_numbers = []
        names = []
        for part in query.split():
            if '@' in part:
                emails.append(part)
            elif is_phone_number(part):
                phone_numbers.append(part)
            else:
                names.append(part)

        q = models.Q()

        for email in emails:
            q &= (
                models.Q(email__iexact=email)
                | models.Q(legal_representatives__email__iexact=email)
            )

        for phone_number in phone_numbers:
            q &= (
                models.Q(phone_number=phone_number)
                | models.Q(phone_number_alternative=phone_number)
                | models.Q(legal_representatives__phone_number=phone_number)
                | models.Q(legal_representatives__phone_number_alternative=phone_number)
            )

        for name in names:
            q &= (
                self.q_match_name(name, 'first')
                | self.q_match_name(name, 'last')
                | self.q_match_name(name, 'legal_representatives__first')
                | self.q_match_name(name, 'legal_representatives__last')
            )

        # We do not want to allow overly generic queries. So if neither
        # an email nor a phone number have been included, a full name must
        # match.
        if not emails and not phone_numbers:
            q &= (
                self.q_name_is_matched(names, 'first')
                & self.q_name_is_matched(names, 'last')
            ) | (
                self.q_name_is_matched(names, 'legal_representatives__first')
                & self.q_name_is_matched(names, 'legal_representatives__last')
            )

        return self.filter(q).distinct()


class BaseContact(TimeStampedModel):
    first_name = models.CharField(_('First name'), max_length=64)
    last_name = models.CharField(_('Last name'), max_length=64)
    title = models.CharField(_('Title'), max_length=64, blank=True)

    date_of_birth = DateField(_('Date of birth'), blank=True, null=True)
    phone_number = PhoneNumberField(_('Phone number'), max_length=32, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return ' '.join(filter(None, [self.title, self.first_name, self.last_name]))

    @property
    def short_name(self):
        # a bit simplistic, but should be sufficient
        return f'{self.first_name[0]}. {self.last_name}'


class Contact(BaseContact):
    subject_uuid = models.UUIDField(unique=True, editable=False, default=None)

    first_name_phonetic = models.CharField(max_length=128, editable=False, default=None)
    last_name_phonetic = models.CharField(max_length=128, editable=False, default=None)

    email = models.EmailField(_('Email'), max_length=128, blank=True)
    phone_number_alternative = PhoneNumberField(
        _('Phone number alternative'), max_length=32, blank=True
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
        )

    @property
    def is_reachable(self):
        return any([
            self.get_address(),
            self.phone_number,
            self.email,
            [c for c in self.legal_representatives.all() if not c.subject.blocked],
        ])

    @property
    def is_underage(self):
        if not self.date_of_birth:
            return None
        delta = relativedelta(years=settings.CASTELLUM_FULL_AGE)
        return self.date_of_birth + delta > datetime.date.today()

    @cached_property
    def is_legal_representative(self):
        return self.id and self.legal_representative_of.exists()

    @cached_property
    def has_legal_representative(self):
        return self.id and self.legal_representatives.exists()

    def get_legal_representatives_tree(self, path=()):
        path = [*path, self.pk]
        children = []
        for c in self.legal_representatives.exclude(pk__in=path).order_by('pk'):
            subtree = c.get_legal_representatives_tree(path)
            children.append((c, subtree))
        return children

    @cached_property
    def legal_representatives_transitive(self):
        # ordered breadth first
        i = 0
        seen = [self]
        while i < len(seen):
            for c in seen[i].legal_representatives.order_by('pk'):
                if c not in seen:
                    seen.append(c)
            i += 1
        return seen[1:]

    @cached_property
    def email_recipients(self):
        if self.email:
            return [self]
        else:
            return [
                c
                for c in self.legal_representatives_transitive
                if c.email and not c.subject.blocked
            ]

    @cached_property
    def own_or_legal_representative_emails(self):
        return list(set(c.email for c in self.email_recipients))

    @cached_property
    def email_recipients_string(self):
        if len(self.email_recipients) > 1:
            return ', '.join(c.full_name for c in self.email_recipients)
        return ''

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
    zip_code = models.CharField(_('Postal code'), max_length=12)
    street = models.CharField(_('Street'), max_length=128)
    house_number = models.CharField(_('House number'), max_length=16)
    additional_information = models.CharField(
        _('Additional address information'), max_length=32, blank=True
    )

    def lines(self):
        line1 = ' '.join(
            [self.street, self.house_number, self.additional_information]
        ).strip()
        line2 = f'{self.zip_code} {self.city}'
        return line1, line2

    def __str__(self):
        return '{}, {}'.format(*self.lines())

    class Meta:
        ordering = [
            'country',
            'city',
            'zip_code',
            'street',
            'house_number',
            'additional_information',
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
            date_of_birth=self.date_of_birth,
            phone_number=self.phone_number,
            email=self.email,
        )
