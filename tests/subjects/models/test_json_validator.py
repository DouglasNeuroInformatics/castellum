import json
from io import BytesIO
from pathlib import Path

import pytest

from castellum.studies.models import GEOJSON_SCHEMA
from castellum.utils.forms import JsonFileValidator


def get_empty_validator():
    basic_json = """{
        "$defs": {
            "test": {}
        }
    }"""

    basic_ref = '#/$defs/test'

    return JsonFileValidator(json.loads(basic_json), basic_ref)


def get_geofilter_validator():
    return JsonFileValidator(GEOJSON_SCHEMA, '#/$defs/geofilter')


def test_basic_json():
    get_empty_validator()(BytesIO(b'{}'))


@pytest.mark.xfail
def test_invalid_json():
    get_empty_validator()(BytesIO(b'{{}'))


@pytest.mark.parametrize('geojson_filename', [
        'feature-collection.geojson',
        'feature-multipolygon.geojson',
        'feature-point.geojson',
        'feature-polygon.geojson',
        'feature-polygon-with-hole.geojson',
])
def test_all_jsons_are_valid(geojson_filename):
    """This test is here just to make sure that the test geo-jsons contain valid json,
    so an x-fail is not a false positive."""
    here = Path(__file__).parent
    geojson = Path(here, 'geojson_test_files', geojson_filename)

    with open(geojson, 'rb') as geojson_file:
        get_empty_validator()(geojson_file)


@pytest.mark.parametrize('geojson_filename', [
        'feature-collection.geojson',
        'feature-multipolygon.geojson',
        pytest.param('feature-point.geojson', marks=pytest.mark.xfail(strict=True)),
        'feature-polygon.geojson',
        'feature-polygon-with-hole.geojson',
])
def test_jsons_are_valid_geofilters(geojson_filename):
    """Test that different features pass or fail based on the geofilter definition."""
    here = Path(__file__).parent
    geojson = Path(here, 'geojson_test_files', geojson_filename)

    with open(geojson, 'rb') as geojson_file:
        get_geofilter_validator()(geojson_file)
