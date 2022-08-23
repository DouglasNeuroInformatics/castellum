"""Import subjects from a CSV file into Castellum.

Customize this script and copy it to ``castellum/subjects/management/commands/``,
You can then execute it using ``django-admin import_subjects``.
"""

import csv
import datetime
import sys

from django import forms
from django.core.management.base import BaseCommand
from django.db import transaction

from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.subjects.models import Subject

SOURCE = 'import {}'.format(datetime.date.today())
ADDRESS_MAP = {}
CONTACT_MAP = {
    'first_name': 0,
    'last_name': 1,
    'date_of_birth': 2,
}
SUBJECT_MAP = {}
ATTRIBUTES_MAP = {
    'd1': 3,
}


def create(model, data, **extra):
    form_cls = forms.modelform_factory(model, fields=data.keys())
    form = form_cls(data)
    for key, value in extra.items():
        setattr(form.instance, key, value)
    if not form.is_valid():
        raise ValueError(form.errors.as_json())
    return form.save()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        with open(options['path']) as fh:
            rows = csv.reader(fh)
            out = csv.writer(self.stdout)

            for row in rows:
                try:
                    attributes = {key: row[i] for key, i in ATTRIBUTES_MAP.items() if row[i]}
                    subject_data = {key: row[i] for key, i in SUBJECT_MAP.items() if row[i]}
                    contact_data = {key: row[i] for key, i in CONTACT_MAP.items() if row[i]}
                    address_data = {key: row[i] for key, i in ADDRESS_MAP.items() if row[i]}

                    if Contact.objects.filter(**contact_data).exists():
                        raise ValueError('potential duplicate')

                    with transaction.atomic():
                        with transaction.atomic(using='contacts'):
                            subject_data['attributes'] = attributes
                            subject_data['source'] = SOURCE
                            subject = create(Subject, subject_data)

                            contact = create(Contact, contact_data, subject_uuid=subject.uuid)

                            if address_data:
                                create(Address, address_data, contact_id=contact.id)
                except Exception as e:
                    if options['verbosity'] > 0:
                        self.stderr.write(str(e))
                    out.writerow(row)
