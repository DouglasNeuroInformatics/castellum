# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


def delete_study_domain(sender, instance, using, **kwargs):
    from castellum.studies.models import Study

    if sender is Study:
        instance.domains.all().delete()


def create_session_domain(sender, instance, using, **kwargs):
    from castellum.pseudonyms.models import Domain
    from castellum.studies.models import StudySession

    if sender is StudySession and not instance.domains.exists():
        Domain.objects.create(
            bits=settings.CASTELLUM_SESSION_DOMAIN_BITS,
            context=instance,
        )


def delete_session_domain(sender, instance, using, **kwargs):
    from castellum.studies.models import StudySession

    if sender is StudySession:
        instance.domains.all().delete()
