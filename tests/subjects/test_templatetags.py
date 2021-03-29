from urllib.parse import parse_qs
from urllib.parse import urlparse

from castellum.subjects.templatetags import subjects as tags


def test_delete_mail_uri(participation):
    url = tags.delete_mail_uri(participation)

    data = urlparse(url)
    assert data.scheme == 'mailto'
    assert data.path == participation.study.email

    query = parse_qs(data.query)
    assert query['body'][0].startswith('We received a deletion request')
