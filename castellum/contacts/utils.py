# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import cologne_phonetics
from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers.phonenumberutil import NumberParseException


def phonetic(s, encode=True):
    codes = [code for __, code in cologne_phonetics.encode(s)]
    if encode:
        return ':' + ':'.join(codes) + ':'
    else:
        return codes


def is_phone_number(part):
    try:
        PhoneNumber.from_string(part)
        return True
    except NumberParseException:
        return False
