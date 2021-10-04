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

from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from icalendar import Calendar
from icalendar import Event


class BaseCalendarFeed(View):
    token_required = False

    def get(self, request, **kwargs):
        if request.GET.get('format') == 'json':
            return self.get_json(request, **kwargs)
        else:
            return self.get_ics(request, **kwargs)

    def get_json(self, request, **kwargs):
        return JsonResponse({'events': [{
            'title': self.item_title(item),
            'start': self.item_start(item),
            'end': self.item_end(item) if hasattr(self, 'item_end') else None,
            'url': self._item_link(item) if hasattr(self, 'item_link') else None,
        } for item in self.items()]})

    def get_ics(self, request, **kwargs):
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', 'castellum')

        for item in self.items():
            event = Event()
            event.add('uid', request.build_absolute_uri(self.item_uid(item)))
            event.add('dtstamp', self.item_updated_at(item))
            event.add('summary', self.item_title(item))
            event.add('dtstart', self.item_start(item))
            if hasattr(self, 'item_end'):
                event.add('dtend', self.item_end(item))
            if hasattr(self, 'item_link'):
                event.add('url', self._item_link(item))
            if hasattr(self, 'item_description'):
                event.add('description', self.item_description(item))
            elif hasattr(self, 'item_link'):
                event.add('description', self._item_link(item))
            cal.add_component(event)

        response = HttpResponse(content_type='text/calendar')
        response.write(cal.to_ical())
        return response

    def item_updated_at(self, item):
        return timezone.now()

    def item_uid(self, item):
        return self.item_link(item)

    def _item_link(self, item):
        return self.request.build_absolute_uri(self.item_link(item))
