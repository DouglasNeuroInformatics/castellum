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

from .models import Pseudonym
from .models import Subject


def get_subject(pseudonym):
    origin = Pseudonym.objects.get(pseudonym=pseudonym)
    return origin.subject


def get_pseudonym(subject):
    target, __ = Pseudonym.objects.get_or_create(subject=subject)
    return str(target.pseudonym)


def create_pseudonym():
    subject = Subject.objects.create()
    pseudonym = Pseudonym.objects.create(subject=subject)
    return str(pseudonym.pseudonym)


def delete_pseudonym(pseudonym):
    p = Pseudonym.objects.get(pseudonym=pseudonym)
    p.delete()
