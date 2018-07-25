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

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from pseudonyms.helpers import resolve_pseudonym

from .forms import SubjectForm
from .models import Subject

monitoring_logger = logging.getLogger('monitoring.subject_data')


class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    paginate_by = 20


class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject
    slug_field = 'pseudonym'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributeset_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['contact'], self.object.pseudonym, settings.DOMAINS['attributeset'])
        return context


class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    slug_field = 'pseudonym'

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result
