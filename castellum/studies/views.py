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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views import generic

from . import models


class IndexView(LoginRequiredMixin, generic.ListView):
    model = models.Study
    ordering = 'name'


class CreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Study
    fields = (
        'name',
        'contact_person',
        'summary',
        'expense',
        'test_sessions',
        'test_start',
        'test_end',
        'target_size',
    )

    def get_success_url(self):
        return reverse('studies:index')


class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = models.Study
    fields = (
        'name',
        'contact_person',
        'summary',
        'expense',
        'test_sessions',
        'test_start',
        'test_end',
        'target_size',
    )

    def get_success_url(self):
        return reverse('studies:index')


class PublishView(LoginRequiredMixin, View):
    def post(self, request, study_pk):
        study = get_object_or_404(models.Study, pk=study_pk)
        study.published = not study.published
        study.save()

        return redirect(reverse('studies:index'))
