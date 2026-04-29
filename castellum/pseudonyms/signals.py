# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.models.signals import pre_delete

from castellum.subjects.models import Subject

from .models import KeyPair


def delete_key_pair(sender, instance, using, **kwargs):
    KeyPair.objects.filter(pseudonym__subject=instance).delete()


def register_signal_handlers():
    pre_delete.connect(delete_key_pair, sender=Subject)
