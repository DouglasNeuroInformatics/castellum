# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

from xml.sax.saxutils import escape

COLORS = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33']


def round_max(value):
    s = str(value)
    head = int(s[0])
    tail = 10 ** (len(s) - 1)
    head += 1
    if head & 1:
        head += 1
    return head * tail


class ChartRenderer:
    def __init__(
        self, height=480, width=640, padding=5, colors=COLORS, ui_color='#333'
    ):
        self.height = height
        self.width = width
        self.padding = padding
        self.colors = colors
        self.ui_color = ui_color

        self.char_width = 10
        self.char_padding = 4
        self.x_labels = self.char_width * 5
        self.y_labels = 20
        self.y_legend = 20

    def get_color(self, i):
        return self.colors[i % len(self.colors)]

    def attrs(self, **kwargs):
        return ''.join(
            ' {}="{}"'.format(key.replace('_', '-'), escape(str(value)))
            for key, value in sorted(kwargs.items())
        )

    def element(self, tag, content=None, **attrs):
        if content:
            if '\n' in content:
                lines = content.strip().split('\n')
                content = '\n' + '\n'.join('\t' + l for l in lines) + '\n'
            return '<{tag}{attrs}>{content}</{tag}>\n'.format(
                tag=tag,
                attrs=self.attrs(**attrs),
                content=content,
            )
        else:
            return '<{tag}{attrs} />\n'.format(
                tag=tag,
                attrs=self.attrs(**attrs),
            )

    def line(self, x1, x2, y1, y2, color, **kwargs):
        return self.element(
            'line', x1=x1, x2=x2, y1=y1, y2=y2, stroke=color, **kwargs)

    def text(self, s, x, y, **kwargs):
        return self.element(
            'text', escape(str(s)), x=x, y=y, fill=self.ui_color, **kwargs)

    def rect(self, x, y, width, height, title=None, **kwargs):
        content = None
        if title:
            content = self.element('title', escape(str(title)))
        return self.element(
            'rect', content, x=x, y=y, width=width, height=height, **kwargs)

    def path(self, points, **kwargs):
        d = 'M {},{} L'.format(*points[0])
        for x, y in points[1:]:
            d += ' {},{}'.format(x, y)
        return self.element('path', d=d, **kwargs)

    def get_title(self, rows, legend, i, j):
        key = rows[i]['label']
        if legend:
            key += ' - ' + legend[j]
        return '{}: {}'.format(key, rows[i]['values'][j])

    def render_axes(self, rows, max_value):
        s = ''
        s += self.line(0, 0, 0, self.height, self.ui_color)
        s += self.line(0, self.width, self.height, self.height, self.ui_color)

        for y, value in [
            (self.height, 0),
            (self.height / 2, max_value // 2),
            (0, max_value),
        ]:
            s += self.text(value, -self.char_padding, y, **{
                'dominant-baseline': 'middle',
                'text-anchor': 'end',
            })

        width = self.width / len(rows)
        y = self.height + self.y_labels / 2
        for i, row in enumerate(rows):
            x = (i + 0.5) * width
            s += self.text(row['label'], x, y, **{
                'dominant-baseline': 'middle',
                'text-anchor': 'middle',
            })

        return s

    def render_legend(self, legend):
        s = ''

        width = 2 * self.char_padding - self.char_width
        for label in legend:
            width += self.char_width + self.char_padding  # square
            width += len(label) * self.char_width  # text
            width += self.char_width  # margin

        x = self.width - width

        s += self.rect(x, -self.y_legend, width, self.y_legend, **{
            'fill': 'none',
            'stroke': self.ui_color,
        })
        x += self.char_padding

        y = -self.y_legend / 2
        for i, label in enumerate(legend):
            # square
            size = self.char_width
            s += self.rect(x, y - size / 2, size, size, fill=self.get_color(i))
            x += self.char_width + self.char_padding
            # text
            s += self.text(label, x, y, **{
                'dominant-baseline': 'middle',
            })
            x += len(label) * self.char_width
            # margin
            x += self.char_width

        return self.element('g', s)

    def render_rows(self, rows, legend, max_value):
        s = ''
        n = len(rows)
        width = self.width / n
        for i, row in enumerate(rows):
            group = ''
            y = self.height - 1
            for j, value in enumerate(row['values']):
                height = self.height * value / max_value
                x = width * (i + 0.5)
                y -= height
                group += self.rect(x - width / 6, y, width / 3, height, **{
                    'fill': self.get_color(j),
                    'stroke': 'white',
                    'title': self.get_title(rows, legend, i, j),
                })
            s += self.element('g', group)
        return s

    def get_view_box(self):
        p = 2 * self.padding
        x = -(self.padding + self.x_labels)
        y = -(self.padding + self.y_legend)
        width = self.width + p + self.x_labels
        height = self.height + p + self.y_legend + self.y_legend
        return '{} {} {} {}'.format(x, y, width, height)

    def render(self, data):
        max_value = max(sum(row['values']) for row in data['rows'])
        max_value = round_max(max_value)

        legend = data.get('legend', [])
        content = ''
        content += self.render_axes(data['rows'], max_value)
        if legend:
            content += self.render_legend(legend)
        content += self.render_rows(data['rows'], legend, max_value)

        return self.element(
            'svg',
            content,
            xmlns='http://www.w3.org/2000/svg',
            viewBox=self.get_view_box(),
        )
