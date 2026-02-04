# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

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
