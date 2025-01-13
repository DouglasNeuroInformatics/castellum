# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


def delete_attribute_data(sender, instance, using, **kwargs):
    from castellum.subjects.models import Subject

    from .models import Attribute

    if sender is Attribute:
        objs = list(Subject.objects.filter(attributes__has_key=instance.json_key))
        for subject in objs:
            del subject.attributes[instance.json_key]
        Subject.objects.bulk_update(objs, ['attributes'])


def sync_date_of_birth(sender, instance, using, **kwargs):
    from castellum.contacts.models import Contact

    if (
        settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID
        and sender is Contact
        and instance.subject_uuid
    ):
        key = f'd{settings.CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID}'
        instance.subject.attributes[key] = instance.date_of_birth
        instance.subject.save()
