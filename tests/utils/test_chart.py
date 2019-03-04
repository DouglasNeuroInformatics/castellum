import pytest

from castellum.utils import chart


def test_chart():
    data = {
        'rows': [{
            'label': 'Apples',
            'values': [3, 2, 5]
        }, {
            'label': 'Oranges',
            'values': [4, 2, 3]
        }, {
            'label': 'Pears',
            'values': [4, 3, 4]
        }, {
            'label': 'Bananas',
            'values': [5, 1, 2]
        }],
        'legend': ['John', 'Jane', 'Joe']
    }

    expected = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-55 -25 700 530">
\t<line x1="0" x2="0" y1="0" y2="480" stroke="#333" />
\t<line x1="0" x2="640" y1="480" y2="480" stroke="#333" />
\t<text x="-4" y="480" fill="#333" dominant-baseline="middle" text-anchor="end">0</text>
\t<text x="-4" y="240.0" fill="#333" dominant-baseline="middle" text-anchor="end">10</text>
\t<text x="-4" y="0" fill="#333" dominant-baseline="middle" text-anchor="end">20</text>
\t<text x="80.0" y="490.0" fill="#333" dominant-baseline="middle" text-anchor="middle">Apples</text>
\t<text x="240.0" y="490.0" fill="#333" dominant-baseline="middle" text-anchor="middle">Oranges</text>
\t<text x="400.0" y="490.0" fill="#333" dominant-baseline="middle" text-anchor="middle">Pears</text>
\t<text x="560.0" y="490.0" fill="#333" dominant-baseline="middle" text-anchor="middle">Bananas</text>
\t<g>
\t\t<rect x="460" y="-20" width="180" height="20" fill="none" stroke="#333" />
\t\t<rect x="464" y="-15.0" width="10" height="10" fill="#e41a1c" />
\t\t<text x="478" y="-10.0" fill="#333" dominant-baseline="middle">John</text>
\t\t<rect x="528" y="-15.0" width="10" height="10" fill="#377eb8" />
\t\t<text x="542" y="-10.0" fill="#333" dominant-baseline="middle">Jane</text>
\t\t<rect x="592" y="-15.0" width="10" height="10" fill="#4daf4a" />
\t\t<text x="606" y="-10.0" fill="#333" dominant-baseline="middle">Joe</text>
\t</g>
\t<g>
\t\t<rect x="53.33333333333333" y="407.0" width="53.333333333333336" height="72.0" fill="#e41a1c" stroke="white">
\t\t\t<title>Apples - John: 3</title>
\t\t</rect>
\t\t<rect x="53.33333333333333" y="359.0" width="53.333333333333336" height="48.0" fill="#377eb8" stroke="white">
\t\t\t<title>Apples - Jane: 2</title>
\t\t</rect>
\t\t<rect x="53.33333333333333" y="239.0" width="53.333333333333336" height="120.0" fill="#4daf4a" stroke="white">
\t\t\t<title>Apples - Joe: 5</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect x="213.33333333333334" y="383.0" width="53.333333333333336" height="96.0" fill="#e41a1c" stroke="white">
\t\t\t<title>Oranges - John: 4</title>
\t\t</rect>
\t\t<rect x="213.33333333333334" y="335.0" width="53.333333333333336" height="48.0" fill="#377eb8" stroke="white">
\t\t\t<title>Oranges - Jane: 2</title>
\t\t</rect>
\t\t<rect x="213.33333333333334" y="263.0" width="53.333333333333336" height="72.0" fill="#4daf4a" stroke="white">
\t\t\t<title>Oranges - Joe: 3</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect x="373.3333333333333" y="383.0" width="53.333333333333336" height="96.0" fill="#e41a1c" stroke="white">
\t\t\t<title>Pears - John: 4</title>
\t\t</rect>
\t\t<rect x="373.3333333333333" y="311.0" width="53.333333333333336" height="72.0" fill="#377eb8" stroke="white">
\t\t\t<title>Pears - Jane: 3</title>
\t\t</rect>
\t\t<rect x="373.3333333333333" y="215.0" width="53.333333333333336" height="96.0" fill="#4daf4a" stroke="white">
\t\t\t<title>Pears - Joe: 4</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect x="533.3333333333334" y="359.0" width="53.333333333333336" height="120.0" fill="#e41a1c" stroke="white">
\t\t\t<title>Bananas - John: 5</title>
\t\t</rect>
\t\t<rect x="533.3333333333334" y="335.0" width="53.333333333333336" height="24.0" fill="#377eb8" stroke="white">
\t\t\t<title>Bananas - Jane: 1</title>
\t\t</rect>
\t\t<rect x="533.3333333333334" y="287.0" width="53.333333333333336" height="48.0" fill="#4daf4a" stroke="white">
\t\t\t<title>Bananas - Joe: 2</title>
\t\t</rect>
\t</g>
</svg>
"""  # noqa

    renderer = chart.ChartRenderer()

    assert renderer.render(data) == expected


@pytest.mark.parametrize('_in,out', [
    (0, 2),
    (1, 2),
    (2, 4),
    (3, 4),
    (79, 80),
    (89, 100),
    (98, 100),
    (99, 100),
    (100, 200),
    (123456, 200000),
])
def test_round_max(_in, out):
    assert chart.round_max(_in) == out
