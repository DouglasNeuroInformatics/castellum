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


def create_domain(bits=40):
    domain = attempt(lambda: Domain.objects.create(bits=bits))
    return domain.key


def delete_domain(domain_key):
    domain = Domain.objects.get(key=domain_key)
    domain.delete()


def get_subject(domain_key, pseudonym):
    return Subject.objects.get(pseudonym__domain__key=domain_key, pseudonym__pseudonym=pseudonym)


def get_pseudonym(subject, target_domain_key):
    target_domain = Domain.objects.get(key=target_domain_key)
    target, __ = attempt(
        lambda: Pseudonym.objects.get_or_create(subject=subject, domain=target_domain)
    )
    return target.pseudonym


def delete_pseudonym(domain_key, pseudonym):
    p = Pseudonym.objects.get(domain__key=domain_key, pseudonym=pseudonym)
    p.subject = None
    p.save()
