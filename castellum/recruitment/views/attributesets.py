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

import logging

from django.shortcuts import get_object_or_404
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import SubjectMixin
from castellum.subjects.models import Subject

from ..forms import AttributeSetForm
from ..models import AttributeDescription
from ..models import AttributeSet
from ..models.attributesets import UNCATEGORIZED

monitoring_logger = logging.getLogger('monitoring.recruitment')


class AttributeSetUpdateView(SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = AttributeSet
    permission_required = 'recruitment.change_attributeset'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        attributeset, __ = queryset.get_or_create(subject=subject, defaults={'data': {}})
        return attributeset

    def get_form_class(self):
        return AttributeSetForm.factory(self.request.user)

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('AttributeSet update: {} by {}'.format(
            self.object.pk,
            self.request.user.pk))
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']

        def get_bound_fields(descriptions):
            for description in descriptions:
                try:
                    yield form['d%i' % description.pk]
                except KeyError:
                    pass

        categories = AttributeDescription.objects.by_category()
        context['uncategorized'] = get_bound_fields(categories.pop(UNCATEGORIZED))
        context['categories'] = {
            category: get_bound_fields(descriptions)
            for category, descriptions in categories.items()
        }

        return context
