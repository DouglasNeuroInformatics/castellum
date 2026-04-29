# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DeleteView
from django.views.generic import ListView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.utils.expressions import exists
from castellum.utils.models import value_set

from ..models import Subject
from ..models import SubjectCreationRequest


class BaseMaintenanceView(PermissionRequiredMixin, ListView):
    model = Subject
    paginate_by = 20
    permission_required = 'subjects.change_subject'

    def get_queryset(self):
        return super().get_queryset().filter(
            filter_queries.to_be_deleted(),
            deceased=False,
            blocked=False,
        )


class MaintenanceAttributesView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_attributes.html'
    tab = 'attributes'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = filter_queries.get_has_missing_attributes(qs)
        return qs.order_by('completeness', 'total')


class MaintenanceDuplicatesView(BaseMaintenanceView):
    model = Contact
    template_name = 'subjects/maintenance_duplicates.html'
    tab = 'duplicates'

    def get_queryset(self):
        to_be_deleted = value_set(
            Subject.objects.filter(to_be_deleted__isnull=False), 'pk'
        )

        return (
            Contact.objects
            .values('first_name', 'last_name')
            .exclude(subject_uuid__in=to_be_deleted)
            .alias(
                count=models.Count('id'),
                date_of_birth_count=models.Count('date_of_birth', distinct=True),
            )
            .filter(
                count__gt=1,
                date_of_birth_count__lt=models.F('count'),
            )
            .order_by('last_name', 'first_name')
        )


class MaintenanceConsentView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_consent.html'
    tab = 'consent'

    def get_by_consent_from_before_full_age(self):
        today = datetime.date.today()

        full_age = Contact.objects.exclude(
            date_of_birth__gt=today - relativedelta(years=settings.CASTELLUM_FULL_AGE),
        )

        return super().get_queryset().filter(
            filter_queries.uuid_filter(full_age),
            filter_queries.has_consent(),
            consent__underage_when_given=True,
        )

    def get_by_deprecated_document(self):
        return (
            super().get_queryset()
            .filter(filter_queries.has_consent())
            .exclude(pk__in=Subject.objects.filter(
                filter_queries.has_consent(exclude_deprecated=True)
            ))
        )

    def get_queryset(self):
        return (
            Subject.objects
            .annotate(
                consent_document_deprecated=exists(
                    self.get_by_deprecated_document(), pk=models.OuterRef('pk')
                ),
                consent_from_before_full_age=exists(
                    self.get_by_consent_from_before_full_age(), pk=models.OuterRef('pk')
                ),
            )
            .exclude(
                consent_document_deprecated=False,
                consent_from_before_full_age=False,
            )
            .select_related('consent__document')
            .order_by('pk')
        )


class MaintenanceReliabilityView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_reliability.html'
    tab = 'reliability'

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate_reliability()
            .annotate(
                ratio=100
                * models.F('reliability_issues')
                / models.F('reliability_total')
            )
            .filter(
                reliability_issues__gt=1,
                ratio__gte=50,
            )
            .order_by('-ratio')
        )


class MaintenanceEstrangedSubjectsView(BaseMaintenanceView):
    template_name = 'subjects/maintenance_estranged_subjects.html'
    tab = 'estranged_subjects'

    def get_queryset(self):
        return super().get_queryset().filter(
            filter_queries.has_consent(include_waiting=True),
            updated_at__lte=(
                timezone.now() - settings.CASTELLUM_ENSTRANGED_SUBJECTS_PERIOD
            ),
        ).order_by('updated_at')


class MaintenanceSubjectCreationRequestView(PermissionRequiredMixin, ListView):
    model = SubjectCreationRequest
    paginate_by = 20
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/maintenance_subjectcreationrequest.html'
    tab = 'subjectcreationrequest'

    def get_queryset(self):
        return (
            SubjectCreationRequest.objects
            .filter(data_is_deleted=False)
            .order_by('created_at')
        )


class SubjectCreationRequestDeleteView(PermissionRequiredMixin, DeleteView):
    model = SubjectCreationRequest
    permission_required = 'subjects.change_subject'
    tab = 'subjectcreationrequest'

    def get_success_url(self):
        return reverse('subjects:maintenance-subjectcreationrequest')

    def get_queryset(self):
        return super().get_queryset().filter(data_is_deleted=False)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mark_as_deleted()
        return redirect(self.get_success_url())
