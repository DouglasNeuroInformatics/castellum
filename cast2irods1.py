"""Get study metadata and subject attributes for all current studies."""

import os
import json

import requests

BASE_DIR = os.getenv('BASE_DIR', 'cast2irods')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
TOKEN = os.getenv('TOKEN', '_YRJeCPMKH2-H7aNOFgTUy0iHCnm-2gp7OznR0qwxro')


def fetch(path):
    r = requests.get(BASE_URL + path, headers={'Authorization': 'token ' + TOKEN})
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    studies = fetch('/studies/api/studies/?status=execution')
    total = len(studies['studies'])
    for i, study_id in enumerate(studies['studies']):
        print("fetching study %i/%i" % (i + 1, total))
        path = os.path.join(BASE_DIR, str(study_id))
        os.makedirs(path, exist_ok=True)

        info = fetch('/studies/api/studies/%i/' % study_id)
        with open(os.path.join(path, 'study-info.json'), 'w') as fh:
            json.dump(info, fh, indent=4)

        domains = fetch('/execution/api/studies/%i/domains/' % study_id)
        assert len(domains['domains']) == 1
        domain = domains['domains'][0]['key']

        subjects = []
        pseudonyms = fetch('/execution/api/studies/%i/domains/%s/' % (study_id, domain))
        for pseudonym in pseudonyms['pseudonyms']:
            attributes = fetch('/execution/api/studies/%i/domains/%s/%s/attributes/' % (
                study_id, domain, pseudonym
            ))
            subjects.append({'pseudonym': pseudonym, **attributes})

        with open(os.path.join(path, 'subjects.json'), 'w') as fh:
            json.dump(subjects, fh, indent=4)
