from urllib.parse import parse_qs
from urllib.parse import urlparse

from castellum.subjects.templatetags import subjects as tags


def test_delete_mail_uri(user, participation):
    context = {
        'user': user,
    }
    url = tags.delete_mail_uri(context, participation)

    data = urlparse(url)
    assert data.scheme == 'mailto'
    assert data.path == participation.study.email

    query = parse_qs(data.query)
    assert 'we received a deletion request' in query['body'][0]
    assert user.username in query['body'][0]
