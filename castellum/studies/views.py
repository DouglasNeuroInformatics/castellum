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

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.detail import SingleObjectMixin

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.castellum_auth.models import User

from .forms import AddMemberForm
from .forms import MemberForm
from .models import Study
from .models import StudyMembership


class StudyIndexView(PermissionRequiredMixin, ListView):
    model = Study
    ordering = 'name'
    permission_required = 'studies.view_study'


class StudyCreateView(PermissionRequiredMixin, CreateView):
    model = Study
    fields = (
        'name',
        'contact_person',
        'description',
        'expense_allowance',
        'sessions_count',
        'sessions_start',
        'sessions_end',
        'min_subjects_count',
    )
    permission_required = 'studies.add_study'

    def get_success_url(self):
        StudyMembership.objects.get_or_create(
            user=self.request.user, study=self.object)

        return reverse('studies:index')


class StudyUpdateView(PermissionRequiredMixin, UpdateView):
    model = Study
    fields = (
        'name',
        'contact_person',
        'description',
        'expense_allowance',
        'sessions_count',
        'sessions_start',
        'sessions_end',
        'min_subjects_count',
    )
    permission_required = 'studies.change_study'

    def get_success_url(self):
        return reverse('studies:index')


class StudyPublishView(PermissionRequiredMixin, View):
    permission_required = 'studies.change_study'

    def post(self, request, study_pk):
        study = get_object_or_404(Study, pk=study_pk)
        study.published = not study.published
        study.save()

        return redirect(reverse('studies:index'))


class StudyMembersView(PermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Study
    form_class = AddMemberForm
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form(self):
        form = super().get_form()
        form.fields['user'].choices = [(None, '---')] + [
            (user.pk, str(user)) for user in User.objects.exclude(pk__in=self.object.members.all())]
        return form

    def get_success_url(self):
        return reverse('studies:members', args=[self.object.pk])

    def form_valid(self, form):
        StudyMembership.objects.get_or_create(
            user=form.cleaned_data['user'], study=self.object)
        return super().form_valid(form)


class StudyMemberUpdateView(PermissionRequiredMixin, UpdateView):
    model = StudyMembership
    form_class = MemberForm
    permission_required = 'studies.change_study'

    def get_success_url(self):
        return reverse('studies:members', args=[self.object.study.pk])
