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

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.views.generic import ListView
from django.views.generic import TemplateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentConfirmation
from castellum.subjects.models import Subject

from .models import MonitoringEntry


class DataProtectionView(PermissionRequiredMixin, TemplateView):
    template_name = 'data_protection/index.html'
    permission_required = [
        'subjects.view_subject',
        'castellum_auth.privacy_level_2',
    ]
    tab = 'dashboard'
    limit_by = 10

    def get_to_be_deleted(self):
        subjects = Subject.objects.filter(to_be_deleted__isnull=False).annotate(
            deletion_due=models.ExpressionWrapper(
                models.F('to_be_deleted') + settings.CASTELLUM_SUBJECT_DELETION_PERIOD,
                output_field=models.DateTimeField(),
            )
        )

        return subjects[:self.limit_by], max(subjects.count() - self.limit_by, 0)

    def get_orphans(self):
        candidates = Subject.objects\
            .annotate(pr_count=models.Count('participationrequest', filter=~models.Q(
                participationrequest__status=ParticipationRequest.UNSUITABLE
            )))\
            .filter(no_recruitment=True, pr_count=0)

        subjects = []
        for subject in candidates:
            if len(subjects) >= self.limit_by:
                break
            if not subject.contact.guardian_of.exists():
                subjects.append(subject)

        # no way to efficiently determine missing
        return subjects, 0

    def get_unreachable(self):
        contacts = Contact.objects\
            .annotate(guardian_count=models.Count('guardians'))\
            .filter(
                guardian_count=0,
                address=None,
                email='',
                phone_number='',
            )\
            .order_by()
        subjects = []
        for contact in contacts[:self.limit_by]:
            subjects.append(contact.subject)

        return subjects, max(contacts.count() - self.limit_by, 0)

    def get_no_consent(self):
        acceptable_datetime = timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        subjects = Subject.objects.exclude(
            (
                models.Q(consentconfirmation__status=ConsentConfirmation.CONFIRMED) |
                models.Q(consentconfirmation__updated_at__lte=acceptable_datetime)
            ),
            consentconfirmation__revision=Consent.objects.latest(),
        )

        return subjects[:self.limit_by], max(subjects.count() - self.limit_by, 0)

    def get_studies(self):
        last_acceptable_datetime = timezone.now() - settings.CASTELLUM_STUDY_DELETION_PERIOD
        studies = Study.objects.filter(sessions_end__lte=last_acceptable_datetime)
        return studies[:self.limit_by], max(studies.count() - self.limit_by, 0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['to_be_deleted'], context['to_be_deleted_missing'] = self.get_to_be_deleted()
        context['orphans'], context['orphans_missing'] = self.get_orphans()
        context['unreachable'], context['unreachable_missing'] = self.get_unreachable()
        context['db_consent_uploaded'] = Consent.objects.exists()
        if context['db_consent_uploaded']:
            context['no_consent'], context['no_consent_missing'] = self.get_no_consent()
        context['studies'], context['studies_missing'] = self.get_studies()
        return context


class MonitoringView(PermissionRequiredMixin, ListView):
    model = MonitoringEntry
    tab = 'monitoring'
    template_name = 'data_protection/monitoring.html'
    permission_required = [
        'view_monitoring',
        'castellum_auth.privacy_level_2',
    ]
