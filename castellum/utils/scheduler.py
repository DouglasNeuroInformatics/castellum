# (c) 2018-2021 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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


import datetime

from django.conf import settings
from django.utils import timezone

import requests


def parse_date(s):
    dt = datetime.datetime.fromisoformat(s)
    dt = timezone.make_aware(dt)
    return dt


def request(method, id, token, allowed_status=[]):
    assert settings.SCHEDULER_URL

    url = '{}/api/{}/{}/'.format(settings.SCHEDULER_URL, id, token)
    r = requests.request(method, url, headers={
        'Authorization': 'token ' + settings.SCHEDULER_TOKEN,
    })
    if r.status_code not in allowed_status:
        r.raise_for_status()
    return r


def put(id, token):
    return request('PUT', id, token)


def delete(id, token):
    return request('DELETE', id, token, [404])


def get(id, token):
    r = request('GET', id, token)
    start = r.json().get('datetime')
    return parse_date(start) if start else None


def get_bulk(id):
    url = '{}/api/{}/'.format(settings.SCHEDULER_URL, id)
    r = requests.get(url, headers={
        'Authorization': 'token ' + settings.SCHEDULER_TOKEN,
    })
    r.raise_for_status()
    return {
        key: parse_date(value) if value else None
        for key, value in r.json().items()
    }


def create_invitation_url(id, token):
    put(id, token)  # make sure token exists
    return '{}/invitations/{}/{}/'.format(settings.SCHEDULER_URL, id, token)


def get_schedule_url(id):
    assert settings.SCHEDULER_URL
    return '{scheduler}/{id}/'.format(scheduler=settings.SCHEDULER_URL, id=id)
