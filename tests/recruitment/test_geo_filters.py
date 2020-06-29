from io import StringIO

from django.contrib.gis.geos import Point

import pytest
from model_bakery import baker

from castellum.contacts.models import Contact
from castellum.geofilters.models import Geolocation
from castellum.recruitment import filter_queries
from castellum.studies.models import Study
from castellum.subjects.models import Subject

POLYGON = StringIO("""{
    "properties": null,
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [12, 51],
            [14, 51],
            [14, 53],
            [12, 53],
            [12, 51]
        ]]
    }
}""")

INSIDE = Point(13, 52)
OUTSIDE = Point(3, 20)


def make_contact(point):
    if point is None:
        return baker.make(Contact)
    else:
        location = baker.make(Geolocation, point=point)
        return location.contact


@pytest.mark.django_db
@pytest.mark.parametrize('point,expected', [
    (INSIDE, True),
    (OUTSIDE, False),
    (None, False),
])
def test_geofilter(point, expected):
    make_contact(point)

    study = baker.prepare(Study, geo_filter=POLYGON)
    q = filter_queries.geofilter(study)

    if expected:
        assert Subject.objects.filter(q).exists()
    else:
        assert not Subject.objects.filter(q).exists()


@pytest.mark.django_db
@pytest.mark.parametrize('point1,point2,expected', [
    (INSIDE, INSIDE, 3),
    (INSIDE, OUTSIDE, 1),
    (INSIDE, None, 1),
    (OUTSIDE, OUTSIDE, 0),
    (OUTSIDE, None, 0),
    (None, None, 0),
])
def test_geofilter_with_guardian(point1, point2, expected):
    contact = baker.make(Contact)

    contact.guardians.set([
        make_contact(point1),
        make_contact(point2),
    ])

    study = baker.prepare(Study, geo_filter=POLYGON)
    q = filter_queries.geofilter(study)

    assert Subject.objects.filter(q).count() == expected
