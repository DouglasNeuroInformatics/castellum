# (c) 2018-2021
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

from django.db import models


class MultiDurationExpr(models.Expression):
    """Work around https://code.djangoproject.com/ticket/25287"""

    def __init__(self, dt, duration, factor):
        super().__init__(output_field=models.DateTimeField())
        self.dt = dt
        self.duration = duration
        self.factor = factor

    def get_source_expressions(self):
        return [self.dt, self.factor]

    def set_source_expressions(self, exprs):
        self.dt, self.factor = exprs

    def as_sql(self, *args, **kwargs):
        expr = models.ExpressionWrapper(
            self.dt + self.factor * self.duration, output_field=models.DateTimeField
        )
        return expr.as_sql(*args, **kwargs)

    def as_sqlite(self, compiler, connection):
        microseconds = int(self.duration.total_seconds() * 1_000_000)

        expressions = []
        expression_params = []

        sql, params = compiler.compile(self.dt)
        expressions.append(sql)
        expression_params.extend(params)

        sql, params = compiler.compile(self.factor)
        expressions.append(sql)
        expression_params.extend(params)

        expressions.append('%s')
        expression_params.append(microseconds)

        sql = "django_format_dtdelta('+', {}, {} * {})".format(*expressions)
        return sql, expression_params
