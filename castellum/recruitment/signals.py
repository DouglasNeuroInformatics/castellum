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


def delete_participation_pseudonym(sender, instance, using, **kwargs):
    from castellum.pseudonyms.models import Pseudonym

    from .models import Participation

    if sender is Participation:
        Pseudonym.objects\
            .filter(domain__key=instance.study.domain, subject=instance.subject)\
            .update(subject=None)


def delete_attribute_data(sender, instance, using, **kwargs):
    from castellum.subjects.models import Subject

    from .models import AttributeDescription

    if sender is AttributeDescription:
        objs = list(Subject.objects.filter(attributes__has_key=instance.json_key))
        for subject in objs:
            del subject.attributes[instance.json_key]
        Subject.objects.bulk_update(objs, ['attributes'])
