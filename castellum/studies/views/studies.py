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

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import modelform_factory
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.models import Domain
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Subject
from castellum.utils import Exclusion
from castellum.utils.mail import MailContext
from castellum.utils.views import get_next_url

from ..forms import ImportForm
from ..forms import StudyFilterForm
from ..forms import StudyForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership
from .recruitment import get_related_studies

monitoring_logger = logging.getLogger('monitoring.studies')


def send_pr_mail(study, user_email):
    if not settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_TO or not study.announce_status_changes:
        return 0

    def get_mail_data():
        return {
            'status': study.get_status_display(),
            'previous_status': study.get_previous_status_display(),
            'name': study.name,
            'contact_person': study.contact_person,
            'email': study.email,
            'phone': study.phone,
            'session_types': ', '.join(t.label for t in study.study_type.all()),
            'sessions_start': study.sessions_start,
            'sessions_end': study.sessions_end,
            'excluded_studies': ', '.join(s.name for s in study.excluded_studies.all()),
            'filters': '\n'.join(', '.join(
                str(f) for f in group.subjectfilter_set.all()
            ) for group in study.subjectfiltergroup_set.all()),
            'recruitment_text': study.recruitment_text,
            'exclusion_criteria': study.exclusion_criteria,
        }

    with MailContext('internal') as ctx:
        return ctx.send_mail(
            settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_SUBJECT.format(study=study.name),
            (
                get_mail_data,
                settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_BODY,
                settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_BODY_EN,
            ),
            settings.CASTELLUM_STUDY_STATUS_NOTIFICATION_TO,
            cc=[user_email],
        )


def take_snapshot(study):
    study.snapshot = serializers.serialize('json', [
        study,
        *study.studymembership_set.all(),
        *study.domains.all(),
        *study.studytag_set.all(),
        *study.studysession_set.all(),
        *study.subjectfiltergroup_set.all(),
        *SubjectFilter.objects.filter(group__study=study),
    ], fields=Exclusion(['snapshot']))
    study.save()


class StudyIndexView(LoginRequiredMixin, ListView):
    model = Study
    ordering = 'name'
    paginate_by = 15

    def get(self, request, *args, **kwargs):
        self.form = StudyFilterForm(self.request.GET)
        self.form.full_clean()
        self.form.cleaned_data.setdefault('display', 'list')
        self.form.cleaned_data.setdefault('member', 'my')

        if 'events' in request.GET:
            events = [self.render_event(study) for study in self.get_queryset()]
            return JsonResponse({'events': events})
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):  # noqa: C901
        qs = super().get_queryset()
        q = self.form.cleaned_data.get('q')
        if q:
            for part in q.split():
                qs = qs.filter(
                    models.Q(name__icontains=part) |
                    models.Q(contact_person__icontains=part) |
                    models.Q(principal_investigator__icontains=part) |
                    models.Q(description__icontains=part) |
                    models.Q(studytag__name__icontains=part)
                )
        if self.form.cleaned_data['member'] == 'my':
            qs = qs.filter(studymembership__user=self.request.user)
        if self.form.cleaned_data.get('status'):
            qs = qs.filter(status=self.form.cleaned_data['status'])
        if self.form.cleaned_data.get('type'):
            qs = qs.filter(studysession__type=self.form.cleaned_data['type'])
        if self.form.cleaned_data.get('is_onetime_invitation'):
            qs = qs.filter(is_onetime_invitation=True)
        if self.form.cleaned_data.get('start'):
            qs = qs.filter(sessions_end__gte=self.form.cleaned_data['start'].date())
        if self.form.cleaned_data.get('end'):
            qs = qs.filter(sessions_start__lte=self.form.cleaned_data['end'].date())
        return qs.distinct()

    def render_event(self, study):
        return {
            'start': study.sessions_start,
            'end': study.sessions_end,
            'title': study.name,
            'url': reverse('studies:detail', args=[study.pk]),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class StudyDetailView(PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.view_study'
    tab = 'detail'

    def get_permission_object(self):
        # In other views this is handled by StudyMixin. We cannot use
        # that here because this view should not require access_study.
        return self.get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['potential_count'] = (
            Subject.objects.filter(
                filter_queries.study(self.object),
                filter_queries.has_consent()
            ).count()
        )
        context['related_studies'] = list(get_related_studies(self.object))
        return context


class StudyCreateView(PermissionRequiredMixin, CreateView):
    model = Study
    form_class = StudyForm
    permission_required = 'studies.change_study'

    def form_valid(self, form):
        response = super().form_valid(form)

        StudyMembership.objects.get_or_create(user=self.request.user, study=self.object)

        if self.object.is_onetime_invitation:
            self.object.complete_matches_only = True
            self.object.save()

        if self.duplicate:
            self.object.exclusion_criteria = self.duplicate.exclusion_criteria
            self.object.recruitment_text = self.duplicate.recruitment_text
            self.object.advanced_filtering = self.duplicate.advanced_filtering
            self.object.custom_filter = self.duplicate.custom_filter
            self.object.is_exclusive = self.duplicate.is_exclusive
            self.object.complete_matches_only = self.duplicate.complete_matches_only
            self.object.excluded_studies.set(self.duplicate.excluded_studies.all())
            self.object.consent = self.duplicate.consent
            self.object.mail_subject = self.duplicate.mail_subject
            self.object.mail_body = self.duplicate.mail_body
            self.object.email = self.duplicate.email
            self.object.phone = self.duplicate.phone
            self.object.save()

            for session in self.duplicate.studysession_set.all():
                s = self.object.studysession_set.create(
                    name=session.name,
                    duration=session.duration,
                    resource_id=session.resource_id,
                    reminder_text=session.reminder_text,
                )
                s.type.set(session.type.all())

            for name in self.duplicate.tags:
                self.object.studytag_set.create(name=name)

        return response

    def get_success_url(self):
        return reverse('studies:index')

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.duplicate:
            initial['name'] = "Copy " + self.duplicate.name
            initial['contact_person'] = self.duplicate.contact_person
            initial['principal_investigator'] = self.duplicate.principal_investigator
            initial['affiliated_scientists'] = self.duplicate.affiliated_scientists
            initial['affiliated_research_assistants'] = self.duplicate.affiliated_research_assistants  # noqa
            initial['description'] = self.duplicate.description
            initial['is_onetime_invitation'] = self.duplicate.is_onetime_invitation
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.duplicate:
            context['duplicate'] = self.duplicate
        return context

    @cached_property
    def duplicate(self):
        if 'duplicate_pk' not in self.request.GET:
            return None

        duplicate_pk = self.request.GET['duplicate_pk']
        study = get_object_or_404(Study, pk=duplicate_pk)

        perms = ['studies.access_study', 'studies.change_study']
        if not self.request.user.has_perms(perms, study):
            raise PermissionDenied()

        return study


class StudyUpdateView(
    StudyMixin, PermissionRequiredMixin, UpdateView
):
    model = Study
    form_class = StudyForm
    permission_required = 'studies.change_study'
    tab = 'update'

    def get_success_url(self):
        return reverse('studies:update', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'studies/study_base.html'
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyDeleteView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = Study
    permission_required = 'studies.delete_study'
    tab = 'detail'

    def get_success_url(self):
        return reverse('studies:index')

    def delete(self, request, *args, **kwargs):
        monitoring_logger.info(
            'Study {} deleted by {}'.format(self.study.name, self.request.user.pk)
        )
        messages.success(self.request, _('Study has been deleted.'))
        return super().delete(request, *args, **kwargs)


class StudyStartRecruitmentView(StudyMixin, PermissionRequiredMixin, View):
    permission_required = 'studies.view_study'
    is_onetime_invitation = False

    def post(self, request, study_pk):
        # check 'approve_study' without study context to prevent
        # privilege escalation
        if not self.request.user.has_perm('studies.approve_study'):
            raise PermissionDenied

        if self.study.status == self.study.FINISHED:
            return HttpResponseBadRequest()

        if self.study.status == self.study.EXECUTION:
            self.study.set_status(self.study.EDIT)
            monitoring_logger.info(
                'Study {} stopped by {}'.format(self.study.name, self.request.user.pk)
            )
        else:
            self.study.set_status(self.study.EXECUTION)
            take_snapshot(self.study)

            monitoring_logger.info(
                'Study {} started by {}'.format(self.study.name, self.request.user.pk)
            )

        send_pr_mail(self.study, request.user.email)
        return redirect(get_next_url(request, reverse('studies:detail', args=[self.study.pk])))


class StudyFinishRecruitmentView(StudyMixin, PermissionRequiredMixin, View):
    permission_required = 'studies.change_study'

    def post(self, request, study_pk):
        if self.study.status == self.study.FINISHED:
            self.study.restore_previous_status()
        else:
            self.study.set_status(self.study.FINISHED)
            self.study.participation_set\
                .exclude(status=Participation.INVITED)\
                .delete()
        send_pr_mail(self.study, request.user.email)
        return redirect(get_next_url(request, reverse('studies:detail', args=[self.study.pk])))


class StudyPseudonymDomainsView(StudyMixin, PermissionRequiredMixin, TemplateView):
    permission_required = 'studies.change_study'
    template_name = 'studies/study_pseudonym_domains.html'
    tab = 'domains'

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('action') == 'add':
            self.study.domains.create(bits=settings.CASTELLUM_STUDY_DOMAIN_BITS)
        elif self.request.POST.get('action') == 'name':
            domain = get_object_or_404(self.study.domains.all(), key=self.request.POST['domain'])
            form_cls = modelform_factory(Domain, fields=['name'])
            form = form_cls(data=self.request.POST, instance=domain)
            if form.is_valid():
                form.save()

        return redirect('studies:domains', self.study.pk)


class StudyImportView(PermissionRequiredMixin, FormView):
    permission_required = 'studies.change_study'
    template_name = 'studies/study_import.html'
    form_class = ImportForm

    def render_person(self, person):
        return person.get('name', person.get('email'))

    def render_persons(self, persons):
        return ', '.join([s for s in [self.render_person(p) for p in persons] if s])

    def form_valid(self, form):
        # Not every JSON input that is valid according to the schema is
        # also valid according to the model. So we send the input to
        # ``StudyCreateView`` to also check the model restrictions. If
        # there are any issues, that view will provide helpful error
        # messages to users.

        json = form.cleaned_data['json']

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
            'min_subject_count': json.get('number_participants_expected'),
        })
        self.request.POST.setlist('tags', json.get('keywords', []))

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
            'keywords': list(self.study.tags),
            'type': [t for t in self.study.study_type.values_list('export_key', flat=True) if t],
        }

        response = JsonResponse({k: v for k, v in data.items() if v})
        filename = 'castellum_{}.json'.format(slugify(self.study.name))
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


class StudyDiffView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.approve_study'
    template_name = 'studies/study_diff.html'
    tab = 'diff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['snapshot'] = list(serializers.deserialize(
                'json', self.study.snapshot, ignorenonexistent=True
            ))
        except serializers.base.DeserializationError:
            context['snapshot'] = []
        return context
