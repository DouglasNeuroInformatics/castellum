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

from django.core.management.base import BaseCommand

from castellum.contacts.models import Contact


class Command(BaseCommand):
    help = 'Delete a subject with all of their data.'

    def add_arguments(self, parser):
        parser.add_argument('first_name')
        parser.add_argument('last_name')

    def handle(self, *args, **options):
        contact = Contact.objects.get(
            first_name=options['first_name'],
            last_name=options['last_name'],
        )

        contact.subject.delete()
