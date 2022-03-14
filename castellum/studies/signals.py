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
