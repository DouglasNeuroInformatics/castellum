import pytest

import castellum


def parse_version(s):
    return [int(p, 10) for p in s.split('.')]


def skip_old_migration(next_version):
    return pytest.mark.skipif(
        parse_version(castellum.__version__) >= parse_version(next_version),
        reason='test for old migration',
    )
