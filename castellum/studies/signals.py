# (c) 2018-2020
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

from django.conf import settings


def create_study_domain(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import create_domain
    from castellum.studies.models import Study

    if sender is Study and not instance.domain:
        instance.domain = create_domain(settings.CASTELLUM_STUDY_DOMAIN_BITS)


def delete_study_domain(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import delete_domain
    from castellum.studies.models import Study

    if sender is Study and instance.domain:
        delete_domain(instance.domain)


def create_session_domain(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import create_domain
    from castellum.studies.models import StudySession

    if sender is StudySession and not instance.domain:
        instance.domain = create_domain(settings.CASTELLUM_SESSION_DOMAIN_BITS)


def delete_session_domain(sender, instance, using, **kwargs):
    from castellum.pseudonyms.helpers import delete_domain
    from castellum.studies.models import StudySession

    if sender is StudySession and instance.domain:
        delete_domain(instance.domain)
