# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from .models import CodingList
from .models import Pseudonym


def attempt(fn, attempts=10):
    try:
        return fn()
    except IntegrityError:
        if attempts <= 0:
            raise
        return attempt(fn, attempts=attempts - 1)


def get_subject(coding_list_key, pseudonym):
    return Subject.objects.get(
        pseudonym__coding_list__key=coding_list_key,
        pseudonym__pseudonym=pseudonym,
    )


def get_pseudonym(subject, target_coding_list_key):
    target_coding_list = CodingList.objects.get(key=target_coding_list_key)
    target, __ = attempt(
        lambda: Pseudonym.objects.get_or_create(subject=subject, coding_list=target_coding_list)
    )
    return target.pseudonym


def get_pseudonym_if_exists(subject, target_coding_list_key):
    # You should use ``get_pseudonym()`` in most cases as it does not
    # leak whether a pseudony exists.
    target_coding_list = CodingList.objects.get(key=target_coding_list_key)
    target = Pseudonym.objects.filter(subject=subject, coding_list=target_coding_list).first()
    return target.pseudonym if target else None


def delete_pseudonym(coding_list_key, pseudonym):
    p = Pseudonym.objects.get(coding_list__key=coding_list_key, pseudonym=pseudonym)
    p.subject = None
    p.save()
