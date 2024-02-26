import json
from pathlib import Path

import pytest

from castellum.studies.models import GEOJSON_SCHEMA
from castellum.utils.forms import JsonFileValidator


@pytest.mark.parametrize('filename', [
        'feature-collection.geojson',
        'feature-multipolygon.geojson',
        'feature-point.geojson',
        'feature-polygon.geojson',
        'feature-polygon-with-hole.geojson',
])
def test_all_jsons_are_valid(filename):
    """This test is here just to make sure that the test geo-jsons contain valid json,
    so an x-fail is not a false positive."""
    here = Path(__file__).parent
    path = here / 'geojson_test_files' / filename

    with open(path, 'rb') as geojson_file:
        json.load(geojson_file)


@pytest.mark.parametrize('filename', [
        'feature-collection.geojson',
        'feature-multipolygon.geojson',
        pytest.param('feature-point.geojson', marks=pytest.mark.xfail(strict=True)),
        'feature-polygon.geojson',
        'feature-polygon-with-hole.geojson',
])
def test_jsons_are_valid_geofilters(filename):
    """Test that different features pass or fail based on the geofilter definition."""
    here = Path(__file__).parent
    path = here / 'geojson_test_files' / filename
    validator = JsonFileValidator(GEOJSON_SCHEMA, '#/$defs/geofilter')

    with open(path, 'rb') as geojson_file:
        validator(geojson_file)
