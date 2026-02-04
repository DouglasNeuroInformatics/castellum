# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.shortcuts import redirect
from django.utils.translation import check_for_language

from castellum.utils.views import get_next_url

LANGUAGE_QUERY_PARAMETER = 'language'


def set_language(request):
    """Save language in the user model.

    See also django.views.i18n.set_language
    """
    if request.method == 'POST' and request.user.is_authenticated:
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            request.user.language = lang_code
            request.user.save()

    return redirect(get_next_url(request))
