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

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView


def get_stats():
    for ct in ContentType.objects.all():
        cls = ct.model_class()
        if not cls:
            continue
        count = cls.objects.count()

        fields = []
        for field in cls._meta.get_fields():
            if isinstance(field, GenericForeignKey):
                pass  # FIXME
            else:
                try:
                    field_count = cls.objects.exclude(**{field.name: field.get_default()}).count()
                except (AttributeError, ValueError):
                    field_count = cls.objects.exclude(**{field.name: None}).count()
                fields.append({
                    'name': field.name,
                    'count': field_count,
                    'percent': '{}%'.format(field_count * 100 // count) if count != 0 else None,
                })

        yield {
            'name': cls.__name__,
            'count': count,
            'fields': fields,
        }


class ModelStatsView(TemplateView):
    template_name = 'stats/model_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = get_stats()
        return context
