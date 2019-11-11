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

from django import forms
from django.contrib import messages
from django.db import models
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic.detail import SingleObjectMixin

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.castellum_auth.models import User
from castellum.utils.forms import ReadonlyModelForm
from castellum.utils.views import ReadonlyMixin

from ..forms import AddMemberForm
from ..forms import MemberForm
from ..forms import StudyForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership
from ..models import StudySession

monitoring_logger = logging.getLogger('monitoring.studies')


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
                qs = qs.filter(
                    models.Q(name__icontains=part) |
                    models.Q(contact_person__icontains=part) |
                    models.Q(description__icontains=part) |
                    models.Q(keywords__icontains=part) |
                    models.Q(study_type__translations__label__iexact=part)
                )
        if 'all' not in self.request.GET:
            qs = qs.filter(studymembership__user=self.request.user)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['all'] = 'all' in self.request.GET
        return context


class StudyDetailView(PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.view_study'
    tab = 'detail'


class StudyFormMixin:
    model = Study
    form_class = StudyForm

    def get_session_form(self):
        form_class = forms.modelform_factory(StudySession, fields=('duration',))
        return form_class(prefix='{prefix}')

    def get_session_formset(self):
        formset_class = forms.modelformset_factory(
            StudySession, fields=('duration',), form=ReadonlyModelForm, extra=0, can_delete=True,
        )
        kwargs = self.get_form_kwargs()
        study = kwargs.pop('instance', None)
        readonly = kwargs.pop('readonly', False)
        return formset_class(queryset=StudySession.objects.filter(study=study), form_kwargs={
            'readonly': readonly,
        }, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'session_formset' not in context:
            context['session_formset'] = self.get_session_formset()
        context["template_form"] = self.get_session_form()
        return context

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

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)


class StudyUpdateView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, StudyFormMixin, UpdateView
):
    permission_required = 'studies.change_study'
    tab = 'update'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:update', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'studies/study_base.html'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form, session_formset):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, session_formset)


class StudyDeleteView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = Study
    permission_required = 'studies.delete_study'
    tab = 'detail'

    def get_success_url(self):
        return reverse('studies:index')

    def delete(self, request, *args, **kwargs):
        monitoring_logger.info('Study {} deleted by {}'.format(
            self.study.name, self.request.user.pk))
        messages.success(self.request, _('Study has been deleted.'))
        return super().delete(self, request, *args, **kwargs)


class StudyStartRecruitmentView(StudyMixin, PermissionRequiredMixin, View):
    permission_required = 'studies.change_study'

    def post(self, request, study_pk):
        if self.study.status != self.study.FINISHED:
            if self.study.status == self.study.EXECUTION:
                self.study.set_status(self.study.EDIT)
            else:
                self.study.set_status(self.study.EXECUTION)
            return redirect('studies:detail', self.study.pk)
        else:
            return HttpResponseBadRequest()


class StudyFinishRecruitmentView(StudyMixin, PermissionRequiredMixin, View):
    permission_required = 'studies.change_study'

    def post(self, request, study_pk):
        if self.study.status == self.study.FINISHED:
            self.study.restore_previous_status()
        else:
            self.study.set_status(self.study.FINISHED)
        return redirect('studies:detail', self.study.pk)


class StudyRecruitmentSettingsUpdateView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    fields = ('advanced_filtering', 'recruitment_text', 'is_exclusive', 'complete_matches_only')
    permission_required = 'studies.change_study'
    template_name = 'studies/study_recruitmentsettings_form.html'
    tab = 'recruitmentsettings'
    subtab = 'update'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:recruitmentsettings', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExcludedStudiesView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_excluded_studies.html'
    fields = ('excluded_studies',)
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'excluded-studies'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:excluded-studies', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExclusionCriteriaView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_exclusioncriteria.html'
    fields = ('exclusion_criteria',)
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'exclusioncriteria'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:exclusioncriteria', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyMailSettingsView(
    StudyMixin, PermissionRequiredMixin, ReadonlyMixin, UpdateView
):
    model = Study
    template_name = 'studies/study_mailsettings.html'
    fields = ('mail_subject', 'mail_body', 'mail_reply_address',)
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'mailsettings'

    def get_readonly(self):
        return self.object.status == Study.FINISHED

    def get_success_url(self):
        return reverse('studies:mailsettings', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyMembersView(StudyMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Study
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'
    tab = 'members'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.object.status == Study.FINISHED
        return context

    def get(self, request, **kwargs):
        unprivileged_users = list(self.get_unprivileged_members())
        if unprivileged_users:
            messages.warning(self.request, _(
                'Some members of this study with access to filters are blocked from managing '
                'filters due to an insufficient privacy level.\nBlocked users are: '
            ) + ', '.join(user for user in unprivileged_users))
        return self.render_to_response(self.get_context_data())

    def get_form(self):
        choices = [(None, '---')]
        choices.extend([(user.pk, str(user))
                        for user in User.objects.exclude(pk__in=self.object.members.all())])

        form = AddMemberForm(**self.get_form_kwargs())
        form.fields['user'].choices = choices
        return form

    def form_valid(self, form):
        StudyMembership.objects.get_or_create(
            user=form.cleaned_data['user'], study=self.object)
        return HttpResponseRedirect(reverse('studies:members', args=[self.object.pk]))

    def get_unprivileged_members(self):
        max_privacy_level = self.object.get_filter_max_privacy_level()

        for user in self.object.members.all():
            if user.has_perm('recruitment.view_subjectfilter', obj=self.object):
                if user.get_privacy_level() < max_privacy_level:
                    yield user.username


class StudyMembershipUpdateView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = StudyMembership
    form_class = MemberForm
    permission_required = 'studies.change_study'
    study_status = [Study.EDIT, Study.EXECUTION]
    tab = 'members'

    def get_object(self):
        return get_object_or_404(StudyMembership, pk=self.kwargs['pk'], study=self.study)

    def get_success_url(self):
        return reverse('studies:members', args=[self.object.study.pk])


class StudyMembershipRemoveView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = StudyMembership
    permission_required = 'studies.change_study'
    study_status = [Study.EDIT, Study.EXECUTION]
    tab = 'members'

    def get_object(self):
        return get_object_or_404(StudyMembership, pk=self.kwargs['pk'], study=self.study)

    def delete(self, request, *args, **kwargs):
        membership = self.get_object()

        if membership.user.pk == request.user.pk:
            return HttpResponseBadRequest()

        membership.delete()
        return HttpResponseRedirect(reverse('studies:members', args=[membership.study.pk]))
