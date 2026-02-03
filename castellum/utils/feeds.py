# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import View
from icalendar import Calendar
from icalendar import Event


class BaseCalendarFeed(View):
    def get(self, request, **kwargs):
        cal = Calendar()
        cal.add('version', '2.0')
        cal.add('prodid', 'castellum')

        for item in self.items():
            event = Event()
            event.add('uid', self.item_uid(item))
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
            if hasattr(self, 'item_attendees'):
                for user in self.item_attendees(item):
                    event.add('attendee', user.email, {'CN': user.get_full_name()})
            if hasattr(self, 'item_location'):
                event.add('location', self.item_location(item))
            cal.add_component(event)

        response = HttpResponse(content_type='text/calendar')
        response.write(cal.to_ical())
        return response

    def item_updated_at(self, item):
        return timezone.now()

    def _item_link(self, item):
        return self.request.build_absolute_uri(self.item_link(item))
