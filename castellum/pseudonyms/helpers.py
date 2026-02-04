# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db.utils import IntegrityError

from castellum.subjects.models import Subject

from .models import Domain
from .models import Pseudonym


def attempt(fn, attempts=10):
    try:
        return fn()
    except IntegrityError:
        if attempts <= 0:
            raise
        return attempt(fn, attempts=attempts - 1)


def get_subject(domain_key, pseudonym):
    return Subject.objects.get(
        pseudonym__domain__key=domain_key, pseudonym__pseudonym=pseudonym
    )


def get_pseudonym(subject, target_domain_key):
    target_domain = Domain.objects.get(key=target_domain_key)
    target, __ = attempt(
        lambda: Pseudonym.objects.get_or_create(subject=subject, domain=target_domain)
    )
    return target.pseudonym


def get_pseudonym_if_exists(subject, key):
    # You should use ``get_pseudonym()`` in most cases as it does not
    # leak whether a pseudony exists.
    target = Pseudonym.objects.filter( subject=subject, domain__key=key).first()
    return target.pseudonym if target else None


def delete_pseudonym(domain_key, pseudonym):
    p = Pseudonym.objects.get(domain__key=domain_key, pseudonym=pseudonym)
    p.subject = None
    p.save()
