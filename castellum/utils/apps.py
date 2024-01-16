# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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

from django.apps import AppConfig


def patch_django_bootstrap5():
    from django_bootstrap5.renderers import FieldRenderer

    def get_server_side_validation_classes(self):
        # set is-invalid, but not is-valid
        if self.field_errors:
            return 'is-invalid'
        return ''

    FieldRenderer.get_server_side_validation_classes = (
        get_server_side_validation_classes
    )


class UtilsConfig(AppConfig):
    name = 'castellum.utils'

    def ready(self):
        patch_django_bootstrap5()
