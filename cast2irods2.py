"""Get internal pseudonym and attributes for a single subject."""

import argparse
import os

import requests

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
TOKEN = os.getenv('TOKEN', '_YRJeCPMKH2-H7aNOFgTUy0iHCnm-2gp7OznR0qwxro')
GENERAL_DOMAIN = os.getenv('GENERAL_DOMAIN', '35e61660-79e4-45f7-a3d4-a1ab35537b43')


def fetch(path):
    r = requests.get(BASE_URL + path, headers={'Authorization': 'token ' + TOKEN})
    r.raise_for_status()
    return r.json()


def get_subject_data(study_id, study_pseudonym):
    domains = fetch('/execution/api/studies/%i/domains/' % study_id)
    assert len(domains['domains']) == 1
    study_domain = domains['domains'][0]['key']

    pseudonym = fetch('/execution/api/studies/%i/domains/%s/%s/%s/' % (
        study_id, study_domain, study_pseudonym, GENERAL_DOMAIN
    ))['pseudonym']
    attributes = fetch('/subjects/api/subjects/%s/%s/attributes/' % (GENERAL_DOMAIN, pseudonym))
    return {'pseudonym': pseudonym, **attributes}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('study_id', type=int)
    parser.add_argument('pseudonym')
    args = parser.parse_args()

    data = get_subject_data(args.study_id, args.pseudonym)
    print(data)
