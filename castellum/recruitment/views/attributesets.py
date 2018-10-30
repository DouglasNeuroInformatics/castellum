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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.views.generic import UpdateView

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym

from ..forms import AttributeSetForm
from ..models import AttributeSet

monitoring_logger = logging.getLogger('monitoring.recruitment')


class AttributeSetDetailView(LoginRequiredMixin, DetailView):
    model = AttributeSet

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        attributeset, __ = queryset.get_or_create(pseudonym=self.kwargs['slug'])
        return attributeset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_pseudonym'] = resolve_pseudonym(
            AttributeSet.domain, self.object.pseudonym, Contact.domain)
        allowed_fields = AttributeSet.allowed_fields('view', self.request.user)
        context['allowed_fields'] = [field.name for field in allowed_fields]
        return context


class AttributeSetUpdateView(LoginRequiredMixin, UpdateView):
    model = AttributeSet
    slug_field = 'pseudonym'

    def get_form_class(self):
        return AttributeSetForm.factory(self.request.user)

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            AttributeSet.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result
