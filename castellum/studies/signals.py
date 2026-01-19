# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models.signals import pre_delete

from castellum.studies.models import Study
from castellum.studies.models import StudySession


def delete_study_domain(sender, instance, using, **kwargs):
    instance.domains.all().delete()


def delete_session_domain(sender, instance, using, **kwargs):
    instance.domains.all().delete()


def register_signal_handlers():
    pre_delete.connect(delete_study_domain, sender=Study)
    pre_delete.connect(delete_session_domain, sender=StudySession)
