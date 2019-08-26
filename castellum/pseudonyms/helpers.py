# (c) 2018
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

from castellum.subjects.models import Subject

from .models import Domain
from .models import Pseudonym


def create_domain():
    domain = Domain.objects.create()
    return domain.key


def get_subject(domain_key, pseudonym):
    origin = Pseudonym.objects.get(domain__key=domain_key, pseudonym=pseudonym)
    return origin.subject


def get_pseudonym(subject, target_domain_key):
    target_domain = Domain.objects.get(key=target_domain_key)
    target, __ = Pseudonym.objects.get_or_create(subject=subject, domain=target_domain)
    return target.pseudonym


def create_pseudonym(domain_key):
    domain = Domain.objects.get(key=domain_key)
    subject = Subject.objects.create()
    pseudonym = Pseudonym.objects.create(subject=subject, domain=domain)
    return pseudonym.pseudonym


def delete_pseudonym(domain_key, pseudonym, delete_related=False):
    p = Pseudonym.objects.get(domain__key=domain_key, pseudonym=pseudonym)
    if delete_related:
        p.subject.delete()
    else:
        p.delete()
