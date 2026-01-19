# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

import requests
from django.conf import settings
from django.utils import timezone


def parse_date(s):
    dt = datetime.datetime.fromisoformat(s)
    dt = timezone.make_aware(dt)
    return dt


def request(method, id, token, allowed_status=[]):
    assert settings.SCHEDULER_URL

    url = f'{settings.SCHEDULER_URL}/api/{id}/{token}/'
    r = requests.request(method, url, headers={
        'Authorization': f'Bearer {settings.SCHEDULER_TOKEN}',
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
    url = f'{settings.SCHEDULER_URL}/api/{id}/'
    r = requests.get(url, headers={
        'Authorization': f'Bearer {settings.SCHEDULER_TOKEN}',
    })
    r.raise_for_status()
    return {
        key: parse_date(value) if value else None
        for key, value in r.json().items()
    }


def delete_schedule(id):
    url = f'{settings.SCHEDULER_URL}/api/'
    r = requests.delete(url, headers={
        'Authorization': f'Bearer {settings.SCHEDULER_TOKEN}',
    })
    if r.status_code not in [404]:
        r.raise_for_status()
    return r


def create_invitation_url(id, token):
    put(id, token)  # make sure token exists
    return f'{settings.SCHEDULER_URL}/invitations/{id}/{token}/'


def get_schedule_url(id):
    assert settings.SCHEDULER_URL
    return f'{settings.SCHEDULER_URL}/{id}/'
