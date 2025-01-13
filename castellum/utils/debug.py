# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.views import debug

ALLOWED_KEYS = [
    'is_email',
    'unicode_hint',
    'frames',
    'request',
    'exception_type',
    'exception_value',
    'lastframe',
]


class ExceptionReporter(debug.ExceptionReporter):
    def get_traceback_data(self):
        data = super().get_traceback_data()
        return {key: data[key] for key in ALLOWED_KEYS if key in data}
