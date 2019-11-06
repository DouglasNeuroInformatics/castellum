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
from django.views.generic import TemplateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.models import Contact
from castellum.recruitment.models import ParticipationRequest
from castellum.studies.models import Study
from castellum.subjects.models import Consent
from castellum.subjects.models import ConsentConfirmation
from castellum.subjects.models import Subject


class DataProtectionView(PermissionRequiredMixin, TemplateView):
    template_name = 'data_protection/index.html'
    permission_required = 'subjects.view_subject'

    def iter_orphans(self):
        subjects = Subject.objects\
            .annotate(pr_count=models.Count('participationrequest', filter=~models.Q(
                participationrequest__status=ParticipationRequest.UNSUITABLE
            )))\
            .filter(no_recruitment=True, pr_count=0)
        for subject in subjects:
            if not subject.contact.guardian_of.exists():
                yield subject

    def iter_unreachable(self):
        contacts = Contact.objects\
            .annotate(guardian_count=models.Count('guardians'))\
            .filter(
                guardian_count=0,
                address=None,
                email='',
                phone_number='',
            )
        for contact in contacts:
            yield contact.subject

    def get_no_consent(self):
        acceptable_datetime = timezone.now() - settings.CASTELLUM_CONSENT_REVIEW_PERIOD
        return Subject.objects.exclude(
            (
                models.Q(consentconfirmation__status=ConsentConfirmation.CONFIRMED) |
                models.Q(consentconfirmation__updated_at__lte=acceptable_datetime)
            ),
            consentconfirmation__revision=Consent.objects.latest(),
        )

    def get_context_data(self, **kwargs):
        study_last_acceptable_datetime = timezone.now() - settings.CASTELLUM_STUDY_DELETION_PERIOD
        context = super().get_context_data(**kwargs)
        context['to_be_deleted'] = Subject.objects.filter(to_be_deleted=True)
        context['orphans'] = list(self.iter_orphans())
        context['unreachable'] = list(self.iter_unreachable())
        if Consent.objects.exists():
            context['no_consent'] = self.get_no_consent()
        context['studies'] = Study.objects.filter(
            sessions_end__lte=study_last_acceptable_datetime)
        return context
