# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.forms import modelform_factory
from django.http import Http404
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.audit.helpers import audit
from castellum.audit.models import AuditEvent
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.models import Domain
from castellum.pseudonyms.models import Pseudonym
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.subjects.models import Subject
from castellum.utils import scheduler
from castellum.utils.views import BaseProtectedMediaView
from castellum.utils.views import get_next_url

from ..forms import StudyFilterForm
from ..forms import StudyForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership


class StudyIndexView(LoginRequiredMixin, ListView):
    model = Study
    ordering = ['-created_at', 'name']
    paginate_by = 20

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

    def q_action_required(self):
        today = datetime.date.today()
        return (
            (models.Q(sessions_end=None) & ~models.Q(status=Study.FINISHED))
            | (models.Q(sessions_end__lt=today) & ~models.Q(status=Study.FINISHED))
            | (models.Q(pseudonyms_delete_date=None) & ~models.Q(domains=None))
            | (models.Q(pseudonyms_delete_date__lt=today) & ~models.Q(domains=None))
        )

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.form.cleaned_data.get('q')
        if q:
            for part in q.split():
                qs = qs.filter(
                    models.Q(name__icontains=part)
                    | models.Q(contact_person__icontains=part)
                    | models.Q(principal_investigator__icontains=part)
                    | models.Q(description__icontains=part)
                    | models.Q(studytag__name__icontains=part)
                )
        if self.form.cleaned_data.get('member') != 'all':
            member = self.form.cleaned_data['member']
            if member != 'my' and self.request.user.is_superuser:
                qs = qs.filter(studymembership__user__username=member)
            else:
                qs = qs.filter(studymembership__user=self.request.user)
        if self.form.cleaned_data.get('status'):
            status = self.form.cleaned_data['status']
            if status == 'action-required':
                qs = qs.filter(self.q_action_required())
            else:
                qs = qs.filter(status=status)
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
            'min_subject_count': study.min_subject_count,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class StudyDetailView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.view_study'
    require_member = False
    tab = 'detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['potential_count'] = Subject.objects.filter(
            filter_queries.study_recruitable(self.object),
            filter_queries.already_in_study(self.object, include_recruitment=False),
        ).count()
        return context


class StudyCreateView(PermissionRequiredMixin, CreateView):
    model = Study
    form_class = StudyForm
    permission_required = 'studies.change_study'

    def form_valid(self, form):
        response = super().form_valid(form)

        StudyMembership.objects.get_or_create(user=self.request.user, study=self.object)

        if self.duplicate:
            # copy all fields that are not part of the create form
            self.object.recruitment_text = self.duplicate.recruitment_text
            self.object.advanced_filtering = self.duplicate.advanced_filtering
            self.object.is_exclusive = self.duplicate.is_exclusive
            self.object.complete_matches_only = self.duplicate.complete_matches_only
            self.object.excluded_studies.set(self.duplicate.excluded_studies.all())
            self.object.included_studies.set(self.duplicate.included_studies.all())
            self.object.mail_subject = self.duplicate.mail_subject
            self.object.mail_body = self.duplicate.mail_body
            self.object.save()

            self.object.general_domains.set(self.duplicate.general_domains.all())

            for domain in self.duplicate.domains.all():
                Domain.objects.create(
                    name=domain.name,
                    bits=domain.bits,
                    content_type=domain.content_type,
                    object_id=self.object.pk,
                )

            for session in self.duplicate.studysession_set.order_by('pk'):
                s = self.object.studysession_set.create(
                    name=session.name,
                    duration=session.duration,
                    reminder_text=session.reminder_text,
                    first_reminder_days=session.first_reminder_days,
                    second_reminder_days=session.second_reminder_days,
                )
                s.type.set(session.type.all())
                s.resources.set(session.resources.all())

            for tag in self.duplicate.executiontag_set.all():
                self.object.executiontag_set.create(name=tag.name, color=tag.color)
        else:
            Domain.objects.create(
                bits=settings.CASTELLUM_STUDY_DOMAIN_BITS,
                context=self.object,
            )

            for name, color in settings.CASTELLUM_DEFAULT_EXECUTION_TAGS:
                self.object.executiontag_set.create(name=name, color=color)

        return response

    def get_success_url(self):
        return reverse('studies:detail', args=[self.object.pk])

    def post(self, request, *args, **kwargs):
        self.object = None
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.duplicate:
            initial['contact_person'] = self.duplicate.contact_person
            initial['principal_investigator'] = self.duplicate.principal_investigator
            initial['affiliated_scientists'] = self.duplicate.affiliated_scientists
            initial['affiliated_research_assistants'] = (
                self.duplicate.affiliated_research_assistants
            )
            initial['phone'] = self.duplicate.phone
            initial['email'] = self.duplicate.email
            initial['description'] = self.duplicate.description
            initial['url'] = self.duplicate.url
            initial['tags'] = list(self.duplicate.tags)
            initial['min_subject_count'] = self.duplicate.min_subject_count
            initial['exportable_attributes'] = list(
                self.duplicate.exportable_attributes.all()
            )
        if self.request.method == 'GET':
            initial.update(self.request.GET.dict())
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


class StudyUpdateView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    form_class = StudyForm
    permission_required = 'studies.change_study'
    tab = 'update'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyDeleteView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = Study
    permission_required = 'studies.delete_study'
    tab = 'detail'

    def get_success_url(self):
        return reverse('studies:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        audit(
            gettext_noop('study deleted'),
            self.request.user.username,
            study_pk=self.study.pk,
        )
        messages.success(self.request, _('Study has been deleted.'))
        return response


class StudyStartRecruitmentView(View):
    def post(self, request, study_pk):
        # check 'approve_study' without study context to prevent
        # privilege escalation
        if not self.request.user.has_perm('studies.approve_study'):
            raise PermissionDenied

        study = get_object_or_404(Study, pk=study_pk)
        if study.status == study.FINISHED:
            return HttpResponseBadRequest()

        if study.status == study.EXECUTION:
            study.set_status(study.DRAFT)
            audit(
                gettext_noop('study stopped'),
                request.user.username,
                study_pk=study.pk,
            )
        else:
            study.set_status(study.EXECUTION)
            audit(
                gettext_noop('study started'),
                request.user.username,
                study_pk=study.pk,
            )

        return redirect(
            get_next_url(request, reverse('studies:detail', args=[study.pk]))
        )


class StudyFinishRecruitmentView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'studies.change_study'
    template_name = 'studies/study_finish.html'
    tab = 'detail'

    def get(self, request, **kwargs):
        if self.study.status == self.study.FINISHED:
            raise Http404
        return super().get(request, **kwargs)

    def post(self, request, study_pk):
        if self.study.status == self.study.FINISHED:
            self.study.restore_previous_status()
            audit(
                gettext_noop('study resumed'),
                request.user.username,
                study_pk=study_pk,
            )
        else:
            self.study.set_status(self.study.FINISHED)
            audit(
                gettext_noop('study finished'),
                request.user.username,
                study_pk=study_pk,
            )

            for session in self.study.studysession_set.all():
                session.domains.all().delete()
                if session.schedule_id:
                    if settings.SCHEDULER_URL:
                        scheduler.delete_schedule(session.schedule_id)
                    session.schedule_id = None
                    session.save()

            Pseudonym.objects.filter(
                domain__in=self.study.domains.all(),
                subject__in=(
                    self.study.participation_set
                    .exclude(status__in=Participation.INVITED_SET)
                    .values('subject')
                ),
            ).update(subject=None)
            self.study.participation_set.exclude(status__in=Participation.INVITED_SET).delete()
        return redirect(
            get_next_url(request, reverse('studies:detail', args=[self.study.pk]))
        )


class StudyDomainsMixin(StudyMixin, PermissionRequiredMixin):
    permission_required = 'studies.change_study'
    tab = 'domains'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['general_domains_exist'] = (
            Domain.objects.filter(object_id=None).exists()
        )
        return context


class StudyDomainsView(StudyDomainsMixin, UpdateView):
    model = Study
    template_name = 'studies/study_domains_study.html'
    fields = ['pseudonyms_delete_date']
    subtab = 'domains-study'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('action') == 'add':
            self.study.domains.create(bits=settings.CASTELLUM_STUDY_DOMAIN_BITS)
        elif self.request.POST.get('action') == 'name':
            domain = get_object_or_404(
                self.study.domains.all(), key=self.request.POST['domain']
            )
            form_cls = modelform_factory(Domain, fields=['name'])
            form = form_cls(data=self.request.POST, instance=domain)
            if form.is_valid():
                form.save()
        else:
            return super().post(request, *args, **kwargs)

        return redirect(self.request.path)


class StudyDomainsGeneralView(StudyDomainsMixin, UpdateView):
    model = Study
    fields = ['general_domains']
    template_name = 'studies/study_domains_general.html'
    subtab = 'domains-general'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyDomainDeleteView(StudyDomainsMixin, DeleteView):
    model = Domain
    template_name = 'studies/domain_confirm_delete.html'
    subtab = 'domains-study'

    def get_object(self):
        return get_object_or_404(self.study.domains.all(), key=self.kwargs['key'])

    def get_success_url(self):
        return reverse('studies:domains', args=[self.study.pk])


class StudyConsentView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    permission_required = 'studies.change_study'
    template_name = 'studies/study_consent.html'
    tab = 'consent'
    fields = ['consent']

    def get_success_url(self):
        return reverse('studies:consent', args=[self.object.pk])

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyAuditTrailView(PermissionRequiredMixin, ListView):
    model = AuditEvent
    permission_required = ['studies.view_audit_trail']
    template_name = 'studies/study_audit_trail.html'
    tab = 'audit-trail'
    paginate_by = 20

    def get_queryset(self):
        self.study = get_object_or_404(Study, pk=self.kwargs.get('study_pk'))
        audit(
            gettext_noop('audit trail accessed'),
            self.request.user.username,
            study_pk=self.study.pk,
        )
        return (
            super().get_queryset()
            .filter(study_pk=self.study.pk)
            .values('created_at__date', 'action', 'username')
            .annotate(created_at=models.Max('created_at'), count=models.Count('id'))
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        return context


class StudyProtectedMediaView(
    StudyMixin, PermissionRequiredMixin, BaseProtectedMediaView
):
    permission_required = []

    def get_path(self):
        return f'studies/{self.study.pk}/{self.kwargs["path"]}'
