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

"""Generate random strings with a checksum.

-   We use an alphabet of length 32 and a checksum of length 2. So the
    probability of a random string from the alphabet passing the check
    is 2**-10 ~= 10**-3.
-   The number of possible strings is 32**(length-2). If we have already
    used 1024 of them and assuming a length of 10, the probability of
    generating a duplicate is 1024 / 32**(10-2) = 2**-30 ~= 10**-9.

"""

import hashlib
import random

from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

CHECK_DIGITS = 2
ALPHABET = '0123456789ACDEFGHJKLMNPQRTUVWXYZ'  # without BIOS for similarity to 8105
HASH = hashlib.md5

safe_random = random.SystemRandom()


def checksum1(msg):
    # Generate a digit that is guaranteed to change on a single input error.
    x = sum(ALPHABET.index(c) for c in msg)
    return ALPHABET[x % len(ALPHABET)]


def checksum2(msg, length):
    h = HASH(msg.encode('ascii')).digest()
    return ''.join(ALPHABET[h[i] % len(ALPHABET)] for i in range(length))


def checksum(msg):
    s = ''
    if CHECK_DIGITS >= 1:
        s += checksum1(msg)
    if CHECK_DIGITS >= 2:
        s += checksum2(msg, CHECK_DIGITS - 1)
    return s


def generate(length=10):
    msg = ''.join(safe_random.choices(ALPHABET, k=length - CHECK_DIGITS))
    return msg + checksum(msg)


def normalize(s):
    return s\
        .upper()\
        .replace('B', '8')\
        .replace('I', '1')\
        .replace('O', '0')\
        .replace('S', '5')


def clean(s):
    s = normalize(s)

    if not all(c in ALPHABET for c in s):
        raise ValidationError(_('Pseudonym contains invalid characters'), code='characters')

    msg = s[:-CHECK_DIGITS]
    actual = s[-CHECK_DIGITS:]
    expected = checksum(msg)
    if actual != expected:
        raise ValidationError(_('Invalid pseudonym'), code='invalid')

    return s
