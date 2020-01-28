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
from django.conf import settings
from django.contrib import messages
from django.db import models
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.http import QueryDict
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

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment import filter_queries
from castellum.recruitment.models import AttributeSet
from castellum.utils.forms import ReadonlyModelForm
from castellum.utils.views import ReadonlyMixin

from ..forms import ImportForm
from ..forms import StudyForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership
from ..models import StudySession
from ..models import StudyType
from .recruitment import get_related_studies

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
        context['enable_export'] = settings.CASTELLUM_ENABLE_STUDY_EXPORT
        return context


class StudyDetailView(PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.view_study'
    tab = 'detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = (
            AttributeSet.objects.filter(
                filter_queries.study(self.object),
                filter_queries.no_recruitment()
            ).count()
        )
        context['related_studies'] = list(get_related_studies(self.object))
        context['enable_export'] = settings.CASTELLUM_ENABLE_STUDY_EXPORT
        return context


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


class StudyImportView(PermissionRequiredMixin, FormView):
    permission_required = 'studies.add_study'
    template_name = 'studies/study_import.html'
    form_class = ImportForm

    def render_person(self, person):
        return person.get('name', person.get('email'))

    def render_persons(self, persons):
        return ', '.join([s for s in [self.render_person(p) for p in persons] if s])

    def form_valid(self, form):
        """
        Not every JSON input that is valid according to the schema is
        also valid according to the model. So we send the input to
        ``StudyCreateView`` to also check the model restrictions. If
        there are any issues, that view will provide helpful error
        messages to users.
        """

        json = form.cleaned_data['json']

        study_types = StudyType.objects\
            .filter(export_key__in=json.get('type', []))\
            .values_list('pk', flat=True)

        self.request.POST = QueryDict(mutable=True)
        self.request.POST.update({
            'name': json['name'],
            'contact_person': self.render_person(json.get('contact_person', {})),
            'principal_investigator': self.render_person(json.get('principal_investigator', {})),
            'affiliated_scientists': self.render_persons(json.get('affiliated_scientists', [])),
            'affiliated_research_assistants': self.render_persons(
                json.get('affiliated_research_assistants', [])
            ),
            'description': json.get('description'),
            'keywords': ', '.join(json.get('keywords', [])),
            'sessions_start': json.get('sessions_start'),
            'sessions_end': json.get('sessions_end'),
            'min_subject_count': json.get('number_participants_expected'),

            # management form is required
            'form-TOTAL_FORMS': 0,
            'form-INITIAL_FORMS': 0,
        })
        self.request.POST.setlist('study_type', study_types)

        create_view = StudyCreateView.as_view()
        return create_view(self.request)


class StudyExportView(StudyMixin, PermissionRequiredMixin, View):
    permission_required = 'studies.view_study'
    STATUS_MAP = {
        Study.EDIT: 'not_started',
        Study.EXECUTION: 'started',
        Study.FINISHED: 'finished',
    }

    def get(self, request, *args, **kwargs):
        data = {
            'name': self.study.name,
            'contact_person': {'name': self.study.contact_person},
            'principal_investigator': {'name': self.study.principal_investigator},
            'description': self.study.description,
            'status': self.STATUS_MAP[self.study.status],
            'sessions_start': self.study.sessions_start,
            'sessions_end': self.study.sessions_end,
            'number_participants_expected': self.study.min_subject_count,
            'type': [t for t in self.study.study_type.values_list('export_key', flat=True) if t],
        }

        response = JsonResponse({k: v for k, v in data.items() if v})
        filename = 'castellum_%s.json' % self.study.name
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        return response
