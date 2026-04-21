from model_bakery import baker

from castellum.recruitment.models import Attribute
from castellum.subjects.management.commands.cleanup_attributes import Command


def test_cleanup_attributes(subject, attribute):
    restricted = baker.make(Attribute, privacy_level=2)

    subject.attributes = {
        attribute.json_key: 1,
        restricted.json_key: 2,
    }
    subject.save()

    cmd = Command()
    cmd.handle(verbosity=0)

    subject.refresh_from_db()
    assert subject.attributes == {
        attribute.json_key: 1,
    }
