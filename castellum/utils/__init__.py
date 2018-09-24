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

LanguageDistribution = namedtuple("LanguageDistribution", ["name", "percentage"])

default_app_config = 'castellum.utils.apps.UtilsConfig'


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


class FakeData:
    def __init__(self):
        self._language = RandomLanguage()

    def language(self):
        return self._language.get()
