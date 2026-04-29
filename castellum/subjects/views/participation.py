# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_noop
from django.views.generic import DeleteView
from django.views.generic import ListView

from castellum.audit.helpers import audit
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.studies.forms import StudyFilterForm
from castellum.studies.mixins import with_study_lock
from castellum.studies.models import Study

from ..mixins import SubjectMixin
from ..models import Subject


class ParticipationListView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = Participation
    template_name = 'subjects/participation_list.html'
    permission_required = 'subjects.list_participations'
    tab = 'participations'
    subtab = 'list'

    def get_queryset(self):
        return (
            self.subject.participation_set
            .filter(status__in=Participation.INVITED_SET)
            .order_by('-updated_at')
        )


class BaseParticipationAddView(SubjectMixin, PermissionRequiredMixin, ListView):
    model = Study
    tab = 'participations'

    def get(self, request, *args, **kwargs):
        self.form = StudyFilterForm(self.request.GET)
        self.form.full_clean()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        q = self.form.cleaned_data.get('q', '')
        if not q:
            return Study.objects.none()

        qs = super().get_queryset()

        for part in q.split():
            qs = qs.filter(
                models.Q(name__icontains=part)
                | models.Q(contact_person__icontains=part)
            )

        # study.p is the list that contains the particiaption (if it exists)
        # or nothing.
        # I did not find a better way to do this.
        return qs.prefetch_related(models.Prefetch(
            'participation_set',
            queryset=self.subject.participation_set.all(),
            to_attr='p',
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class ParticipationRecruitView(BaseParticipationAddView):
    template_name = 'subjects/participation_recruit.html'
    permission_required = 'subjects.view_subject'
    subtab = 'recruit'

    def get_queryset(self):
        perms = ['recruitment.recruit', 'studies.access_study']
        studies = super().get_queryset().filter(status=Study.EXECUTION)

        return studies.filter(pk__in=[
            study.pk for study in studies if (
                self.request.user.has_perms(perms, obj=study)
                and Subject.objects.filter(
                    filter_queries.study_criteria(study), pk=self.subject.pk
                ).exists()
            )
        ])

    @with_study_lock
    def create_participation(self):
        participation, __ = Participation.objects.get_or_create(
            subject=self.subject, study=self.study
        )

        url = reverse('recruitment:contact', args=[self.study.pk, participation.pk])
        return redirect(url)

    def post(self, request, *args, **kwargs):
        self.study = get_object_or_404(
            Study, pk=request.POST['study'], status=Study.EXECUTION
        )

        perms = ['recruitment.recruit', 'studies.access_study']
        if not request.user.has_perms(perms, obj=self.study):
            raise PermissionDenied

        return self.create_participation()


class ParticipationAddView(BaseParticipationAddView):
    template_name = 'subjects/participation_add.html'
    permission_required = 'subjects.add_to_study'
    subtab = 'add'

    @with_study_lock
    def create_participation(self):
        Participation.objects.update_or_create(
            subject=self.subject, study=self.study, defaults={
                'status': Participation.PARTICIPATING,
                'batch': None,
            }
        )

        return self.get(self.request, *self.args, **self.kwargs)

    def post(self, request, *args, **kwargs):
        self.study = get_object_or_404(Study, pk=request.POST['study'])
        return self.create_participation()


class ParticipationDeleteView(SubjectMixin, PermissionRequiredMixin, DeleteView):
    model = Participation
    permission_required = ['subjects.delete_subject']
    tab = 'delete'

    def get_object(self):
        return get_object_or_404(
            Participation, pk=self.kwargs['pk'], subject=self.subject
        )

    def get_success_url(self):
        return reverse('subjects:delete', args=[self.subject.pk])

    def form_valid(self, form):
        response = super().form_valid(form)

        self.subject.pseudonym_set.filter(
            domain__in=self.object.study.domains.all(),
        ).update(subject=None)

        audit(
            gettext_noop('participation deleted'),
            self.request.user.username,
            subject_pk=self.object.subject.pk,
            study_pk=self.object.study.pk,
        )

        return response
