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

from django import forms
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
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
from .models import StudySession


class StudyAccessMixin(PermissionRequiredMixin):
    def get_permission_object(self):
        if hasattr(self, 'object'):
            return self.object
        else:
            return self.get_object()

    def get_permission_required(self):
        permission_required = {'studies.access_study'}
        permission_required.update(super().get_permission_required())
        return permission_required


class StudyMembershipAccessMixin(StudyAccessMixin):
    def get_permission_object(self):
        return super().get_permission_object().study


class StudyIndexView(PermissionRequiredMixin, ListView):
    model = Study
    ordering = 'name'
    permission_required = 'studies.view_study'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            for part in q.split():
                qs = qs.filter(Q(name__icontains=part) | Q(contact_person__icontains=part))
        if 'all' not in self.request.GET:
            qs = qs.filter(studymembership__user=self.request.user)
        return qs

    def get_context_data(self):
        context = super().get_context_data()
        context['q'] = self.request.GET.get('q', '')
        context['all'] = 'all' in self.request.GET
        return context


class StudyFormMixin:
    model = Study
    fields = (
        'name',
        'contact_person',
        'principal_investigator',
        'affiliated_scientists',
        'affiliated_research_assistants',
        'description',
        'keywords',
        'study_type',
        'data_sensitivity',
        'min_subjects_count',
        'expense_allowance',
        'sessions_start',
        'sessions_end',
    )

    def get_session_formset(self):
        formset_class = forms.modelformset_factory(StudySession, fields=('duration',))
        kwargs = self.get_form_kwargs()
        study = kwargs.pop('instance', None)
        return formset_class(queryset=StudySession.objects.filter(study=study), **kwargs)

    def get_context_data(self, **kwargs):
        if 'session_formset' not in kwargs:
            kwargs['session_formset'] = self.get_session_formset()
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        session_formset = self.get_session_formset()
        if form.is_valid() and session_formset.is_valid():
            return self.form_valid(form, session_formset)
        else:
            return self.form_invalid(form, session_formset)

    def form_invalid(self, form, session_formset):
        return self.render_to_response(
            self.get_context_data(form=form, session_formset=session_formset)
        )

    def form_valid(self, form, session_formset):
        response = super().form_valid(form)
        for subform in session_formset:
            subform.instance.study = form.instance
        session_formset.save()
        return response


class StudyCreateView(PermissionRequiredMixin, StudyFormMixin, CreateView):
    permission_required = 'studies.add_study'

    def form_valid(self, form, session_formset):
        response = super().form_valid(form, session_formset)

        StudyMembership.objects.get_or_create(
            user=self.request.user, study=self.object)

        return response

    def get_success_url(self):
        return reverse('studies:index')


class StudyUpdateView(StudyAccessMixin, StudyFormMixin, UpdateView):
    permission_required = 'studies.change_study'

    def get_success_url(self):
        return reverse('studies:index')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class StudyPublishView(StudyAccessMixin, View):
    permission_required = 'studies.change_study'

    def dispatch(self, request, study_pk):
        self.object = get_object_or_404(Study, pk=study_pk)
        return super().dispatch(request, study_pk)

    def post(self, request, study_pk):
        self.object.published = not self.object.published
        self.object.save()

        return redirect(reverse('studies:index'))


class StudyMembersView(StudyAccessMixin, SingleObjectMixin, FormView):
    model = Study
    form_class = AddMemberForm
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        unprivileged_users = list(self.get_unprivileged_members())
        if unprivileged_users:
            messages.warning(self.request, _(
                'One or more study coordinators are blocked from managing filters '
                'due to an insufficient privacy level.\nBlocked users are: '
            ) + ', '.join(user for user in unprivileged_users))
        return super().get(request, *args, **kwargs)

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

    def get_unprivileged_members(self):
        max_privacy_level = self.object.get_filter_max_privacy_level()

        for user in self.object.members.all():
            if user.has_perm('recruitment.view_subjectfilter', obj=self.object):
                if user.get_privacy_level() < max_privacy_level:
                    yield user.username


class StudyMemberUpdateView(StudyMembershipAccessMixin, UpdateView):
    model = StudyMembership
    form_class = MemberForm
    permission_required = 'studies.change_study'

    def get_success_url(self):
        return reverse('studies:members', args=[self.object.study.pk])


class StudyMemberRemoveView(StudyMembershipAccessMixin, DeleteView):
    model = StudyMembership
    permission_required = 'studies.change_study'

    def get_success_url(self):
        return reverse('studies:members', args=[self.object.study.pk])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user.pk != request.user.pk:
            self.object.delete()
        else:
            return HttpResponseBadRequest()
        return HttpResponseRedirect(self.get_success_url())
