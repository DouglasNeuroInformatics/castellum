# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import models
from django.db.models.fields import json


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


@models.JSONField.register_lookup
class ListContainsLookup(json.DataContains):
    """Work around https://code.djangoproject.com/ticket/31836"""

    lookup_name = 'contains'

    def as_sqlite(self, compiler, connection):
        lhs, lhs_params, lhs_key_transforms = self.lhs.preprocess_lhs(
            compiler, connection
        )
        lhs_json_path = json.compile_json_path(lhs_key_transforms)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, lhs_json_path, *rhs_params)
        return (
            f'EXISTS(SELECT (1) FROM JSON_EACH({lhs}, %s) '
            f'WHERE JSON_QUOTE(json_each.value) = {rhs} LIMIT 1)'
        ), params


def exists(qs, **kwargs):
    # workaround for https://code.djangoproject.com/ticket/33482
    if qs.exists():
        return models.Exists(qs.filter(**kwargs))
    else:
        return models.Value(False)
