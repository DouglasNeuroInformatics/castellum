# (c) 2018-2020
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

APP_LABEL = 'geofilters'
DB_LABEL = 'contacts'


class Router:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == APP_LABEL:
            return DB_LABEL

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == APP_LABEL and obj2._meta.app_label == APP_LABEL:
            return True

    def allow_migrate(self, db, app_label, **hints):
        if db == DB_LABEL:
            return app_label == APP_LABEL
        elif app_label == APP_LABEL:
            return False
