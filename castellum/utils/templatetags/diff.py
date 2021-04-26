# (c) 2018-2021
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

from django import template
from django.utils import html

register = template.Library()

TAGS = {
    'diff-added': 'ins',
    'diff-removed': 'del',
}


def register_container_tag(name=None, nargs=0):
    def wrapped(node_class):
        def do(parser, token):
            bits = token.split_contents()
            args = [parser.compile_filter(x) for x in bits[1:]]
            if len(args) != nargs:
                raise template.TemplateSyntaxError(
                    '{tag} tag requires exactly {nargs} arguments'.format(
                        tag=bits[0], nargs=nargs
                    )
                )

            nodelist = parser.parse(['end_' + name])
            parser.delete_first_token()

            return node_class(nodelist, *args)

        register.tag(name=name)(do)
        return node_class

    return wrapped


def get_old(snapshot, new_obj):
    # equality on django models checks only for pk, not actual values
    for old in snapshot:
        if old.object == new_obj:
            return old
    raise KeyError


@register.simple_tag(takes_context=True)
def diff_class(context, new_obj, fieldname):
    snapshot = context['snapshot']
    new_value = getattr(new_obj, fieldname)

    try:
        old = get_old(snapshot, new_obj)
        old_value = getattr(old.object, fieldname)
    except KeyError:
        return 'diff-added'

    if new_value == old_value:
        return 'diff-unchanged'
    elif not new_value:
        return 'diff-removed'
    elif not old_value:
        return 'diff-added'
    else:
        return 'diff-changed'


def diff_get_m2m(snapshot, new_obj, fieldname):
    field = getattr(new_obj, fieldname)
    model = field.model

    try:
        old = get_old(snapshot, new_obj)
        old_values = set(old.m2m_data[fieldname])
    except KeyError:
        old_values = set()

    for obj in field.all():
        if obj.pk in old_values:
            old_values.remove(obj.pk)
            yield obj, 'diff-unchanged'
        else:
            yield obj, 'diff-added'
    for pk in old_values:
        try:
            obj = model.objects.get(pk=pk)
            yield obj, 'diff-removed'
        except model.DoesNotExist:
            # Deletion of related models is not relevant for the diff
            pass


def diff_get_o2m(snapshot, new_obj, fieldname):
    field = getattr(new_obj, fieldname)
    model = field.model

    old_objects = set()
    for old in snapshot:
        if isinstance(old.object, model) and getattr(old.object, field.field.attname) == new_obj.pk:
            old_objects.add(old.object)

    for obj in field.all():
        try:
            old = get_old(snapshot, obj)
            old_objects.remove(obj)
            if str(obj) == str(old.object):
                yield obj, 'diff-unchanged'
            else:
                yield obj, 'diff-changed'
        except KeyError:
            yield obj, 'diff-added'
    for obj in old_objects:
        # Diffing the contents of obj recursively will result in
        # 'diff-unchanged' in this case because this already is the old
        # object.
        yield obj, 'diff-removed'


@register.simple_tag(takes_context=True)
def diff_get(context, new_obj, fieldname):
    snapshot = context['snapshot']
    try:
        rel = getattr(new_obj.__class__, fieldname).rel
        if rel.many_to_many:
            return list(diff_get_m2m(snapshot, new_obj, fieldname))
        else:
            return list(diff_get_o2m(snapshot, new_obj, fieldname))
    except AttributeError:
        cls = diff_class(context, new_obj, fieldname)
        value = getattr(new_obj, fieldname)
        return [(value, cls)]


def _diff_wrap(content, cls):
    tag = TAGS.get(cls, 'span')
    if cls == 'diff-unchanged':
        return content
    return html.format_html('<{0} class="{1}">{2}</{0}>', tag, cls, content)


@register.simple_tag(takes_context=True)
def diff_wrap(context, cls):
    context.setdefault('_diff_wrap_stack', [])
    context['_diff_wrap_stack'].append(cls)

    if cls == 'diff-unchanged':
        return ''
    tag = TAGS.get(cls, 'span')
    return html.format_html('<{0} class="{1}">', tag, cls)


@register.simple_tag(takes_context=True)
def end_diff_wrap(context):
    cls = context['_diff_wrap_stack'].pop()

    if cls == 'diff-unchanged':
        return ''
    tag = TAGS.get(cls, 'span')
    return html.format_html('</{0}>', tag)


@register_container_tag(name='diff_list', nargs=1)
class DiffListNode(template.Node):
    def __init__(self, nodelist, items):
        self.nodelist = nodelist
        self.items = items

    def render(self, context):
        items = self.items.resolve(context)

        def render_item(value, cls):
            with context.push():
                context['value'] = value
                context['class'] = cls
                return self.nodelist.render(context)

        return html.mark_safe(', '.join(
            _diff_wrap(render_item(value, cls), cls) for value, cls in items
        ) or '&mdash;')
