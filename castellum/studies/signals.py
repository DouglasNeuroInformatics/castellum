# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import pre_delete

from castellum.pseudonyms.models import Domain
from castellum.studies.models import Study
from castellum.studies.models import StudySession


def delete_study_domain(sender, instance, using, **kwargs):
    instance.domains.all().delete()


def create_session_domain(sender, instance, using, **kwargs):
    if not instance.domains.exists():
        Domain.objects.create(
            bits=settings.CASTELLUM_SESSION_DOMAIN_BITS,
            context=instance,
        )


def delete_session_domain(sender, instance, using, **kwargs):
    instance.domains.all().delete()


def register_signal_handlers():
    pre_delete.connect(delete_study_domain, sender=Study)
    post_save.connect(create_session_domain, sender=StudySession)
    pre_delete.connect(delete_session_domain, sender=StudySession)
