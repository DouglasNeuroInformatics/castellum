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

    expected = """<svg viewBox="-55 -25 700 530" xmlns="http://www.w3.org/2000/svg">
\t<line stroke="#333" x1="0" x2="0" y1="0" y2="480" />
\t<line stroke="#333" x1="0" x2="640" y1="480" y2="480" />
\t<text dominant-baseline="middle" fill="#333" text-anchor="end" x="-4" y="480">0</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="end" x="-4" y="240.0">10</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="end" x="-4" y="0">20</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="middle" x="80.0" y="490.0">Apples</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="middle" x="240.0" y="490.0">Oranges</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="middle" x="400.0" y="490.0">Pears</text>
\t<text dominant-baseline="middle" fill="#333" text-anchor="middle" x="560.0" y="490.0">Bananas</text>
\t<g>
\t\t<rect fill="none" height="20" stroke="#333" width="180" x="460" y="-20" />
\t\t<rect fill="#e41a1c" height="10" width="10" x="464" y="-15.0" />
\t\t<text dominant-baseline="middle" fill="#333" x="478" y="-10.0">John</text>
\t\t<rect fill="#377eb8" height="10" width="10" x="528" y="-15.0" />
\t\t<text dominant-baseline="middle" fill="#333" x="542" y="-10.0">Jane</text>
\t\t<rect fill="#4daf4a" height="10" width="10" x="592" y="-15.0" />
\t\t<text dominant-baseline="middle" fill="#333" x="606" y="-10.0">Joe</text>
\t</g>
\t<g>
\t\t<rect fill="#e41a1c" height="72.0" stroke="white" width="53.333333333333336" x="53.33333333333333" y="407.0">
\t\t\t<title>Apples - John: 3</title>
\t\t</rect>
\t\t<rect fill="#377eb8" height="48.0" stroke="white" width="53.333333333333336" x="53.33333333333333" y="359.0">
\t\t\t<title>Apples - Jane: 2</title>
\t\t</rect>
\t\t<rect fill="#4daf4a" height="120.0" stroke="white" width="53.333333333333336" x="53.33333333333333" y="239.0">
\t\t\t<title>Apples - Joe: 5</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect fill="#e41a1c" height="96.0" stroke="white" width="53.333333333333336" x="213.33333333333334" y="383.0">
\t\t\t<title>Oranges - John: 4</title>
\t\t</rect>
\t\t<rect fill="#377eb8" height="48.0" stroke="white" width="53.333333333333336" x="213.33333333333334" y="335.0">
\t\t\t<title>Oranges - Jane: 2</title>
\t\t</rect>
\t\t<rect fill="#4daf4a" height="72.0" stroke="white" width="53.333333333333336" x="213.33333333333334" y="263.0">
\t\t\t<title>Oranges - Joe: 3</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect fill="#e41a1c" height="96.0" stroke="white" width="53.333333333333336" x="373.3333333333333" y="383.0">
\t\t\t<title>Pears - John: 4</title>
\t\t</rect>
\t\t<rect fill="#377eb8" height="72.0" stroke="white" width="53.333333333333336" x="373.3333333333333" y="311.0">
\t\t\t<title>Pears - Jane: 3</title>
\t\t</rect>
\t\t<rect fill="#4daf4a" height="96.0" stroke="white" width="53.333333333333336" x="373.3333333333333" y="215.0">
\t\t\t<title>Pears - Joe: 4</title>
\t\t</rect>
\t</g>
\t<g>
\t\t<rect fill="#e41a1c" height="120.0" stroke="white" width="53.333333333333336" x="533.3333333333334" y="359.0">
\t\t\t<title>Bananas - John: 5</title>
\t\t</rect>
\t\t<rect fill="#377eb8" height="24.0" stroke="white" width="53.333333333333336" x="533.3333333333334" y="335.0">
\t\t\t<title>Bananas - Jane: 1</title>
\t\t</rect>
\t\t<rect fill="#4daf4a" height="48.0" stroke="white" width="53.333333333333336" x="533.3333333333334" y="287.0">
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
