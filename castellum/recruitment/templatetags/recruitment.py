# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import hashlib

from django import template

register = template.Library()


@register.simple_tag
def study_legal_representative_hash(study, subject):
    m = hashlib.sha256()
    m.update(str(study.pk).encode('ascii'))
    m.update(str(subject.pk).encode('ascii'))
    return m.hexdigest()
