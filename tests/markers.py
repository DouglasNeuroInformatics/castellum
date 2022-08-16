from django.conf import settings

import pytest
from pkg_resources import parse_version

import castellum


def skip_old_migration(next_version):
    return pytest.mark.skipif(
        parse_version(castellum.__version__) >= parse_version(next_version),
        reason='test for old migration',
    )


def skip_if_geofilters_not_installed():
    return pytest.mark.skipif(
        'castellum.geofilters' not in settings.INSTALLED_APPS,
        reason='app "geocoding" not installed',
    )
