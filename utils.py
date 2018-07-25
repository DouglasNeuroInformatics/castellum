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

from collections import namedtuple
from itertools import chain
from random import choice
from random import randint
from random import random

LanguageDistribution = namedtuple("LanguageDistribution", ["name", "percentage"])


class RandomLanguage:

    distributions = [
        LanguageDistribution("de", 70),
        LanguageDistribution("en", 10),
        LanguageDistribution("tr", 6),
        LanguageDistribution("fr", 6),
        LanguageDistribution("es", 6),
        LanguageDistribution("it", 2),
    ]

    def get(self):
        languages = chain.from_iterable([[l.name]*l.percentage for l in self.distributions])
        return choice(list(languages))


class RandomPhoneNumber:

    def create(self):
        country_code = "+49"
        prefix = self._create_random_number(max_length=4)
        #  smaller cities with longer prefix numbers usually have shorter numbers
        number = self._create_random_number(min_length=5, max_length=9-len(prefix))

        return "{}{}{}".format(country_code, prefix, number)

    def _create_random_number(self, min_length=2, max_length=10):
        number_len = randint(min_length, max_length)
        #  number mustn't start with "0"
        random_number = chain([randint(1, 9)], [randint(0, 9) for _ in range(number_len-1)])
        return "".join(map(str, random_number))


class FakeData:
    def __init__(self):
        self._phone_number = RandomPhoneNumber()
        self._language = RandomLanguage()

    def language(self):
        return self._language.get()

    def phone_number(self):
        return self._phone_number.create()

    def phone_number_by_probability(self, probability=1):
        if random() <= probability:
            return self._phone_number.create()
        return ""
