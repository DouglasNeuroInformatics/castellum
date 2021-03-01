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

"""Import subjects from a CSV file into castellum.

Customize this script and copy it to ``castellum/subjects/management/commands/``,
You can then execute it using ``django-admin import_subjects``.
"""

import csv
import sys

from django import forms
from django.core.management.base import BaseCommand
from django.db import transaction

from castellum.contacts.models import Address
from castellum.contacts.models import Contact
from castellum.recruitment.models import Participation
from castellum.studies.models import Study
from castellum.subjects.models import Subject

SOURCE = 'BASE II'


def convert_date(s):
    if s:
        d, m, y = s.split('.')
        return '{}-{}-{}'.format(y, m, d)


def convert_gender(s):
    if s == 'w':
        return 'f'
    else:
        return s


def create(model, data, **extra):
    form_cls = forms.modelform_factory(model, fields=data.keys())
    form = form_cls(data)
    for key, value in extra.items():
        setattr(form.instance, key, value)
    if not form.is_valid():
        raise ValueError(form.errors.as_json())
    return form.save()


def filter_dict(d):
    return {k: v for (k, v) in d.items() if v and v != 'nein'}


class Command(BaseCommand):
    def handle(self, *args, **options):
        study = Study.objects.create(name=SOURCE)

        rows = csv.reader(sys.stdin, csv.excel_tab)
        out = csv.writer(self.stdout)

        next(rows)  # skip header
        for row in rows:
            try:
                contact_data = filter_dict({
                    'first_name': row[1],
                    'last_name': row[0],
                    'title': row[2],
                    'date_of_birth': convert_date(row[15]),
                    'gender': convert_gender(row[18]),
                    'email': row[13],
                    'phone_number': row[7] + row[8],
                    'phone_number_alternative': row[9] + row[10],
                })
                address_data = filter_dict({
                    'street': row[3],
                    'house_number': row[4],
                    'zip_code': row[5],
                    'city': row[6],
                })

                if Contact.objects.filter(**contact_data).exists():
                    raise ValueError('potential duplicate')

                with transaction.atomic():
                    with transaction.atomic(using='contacts'):
                        subject = Subject.objects.create(source=SOURCE, attributes={})
                        Participation.objects.create(
                            subject=subject, study=study, status=Participation.INVITED
                        )

                        contact = create(Contact, contact_data, subject_id=subject.id)

                        if address_data:
                            create(Address, address_data, contact_id=contact.id)

            except Exception as e:
                if options['verbosity'] > 0:
                    self.stderr.write(str(e))
                out.writerow(row)
