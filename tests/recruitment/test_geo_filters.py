from io import StringIO

from django.contrib.gis.geos import Point

import pytest
from model_bakery import baker

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


@pytest.mark.django_db
@pytest.mark.parametrize('point,expected', [
    (INSIDE, True),
    (OUTSIDE, False),
    (None, False),
])
def test_geofilter(point, expected):
    if point is None:
        baker.make(Subject)
    else:
        baker.make(Geolocation, point=point)

    study = baker.prepare(Study, geo_filter=POLYGON)
    q = filter_queries.geofilter(study)

    if expected:
        assert Subject.objects.filter(q).exists()
    else:
        assert not Subject.objects.filter(q).exists()
