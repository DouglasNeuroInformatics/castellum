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


from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView

from castellum.contacts.models import Contact
from castellum.contacts.views import ContactUpdateView as _ContactUpdateView
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.studies.models import Study

from ..models import AttributeSet
from ..models import ParticipationRequest
from ..utils import get_study_filter_q
from .mixins import PublishedStudyMixin


class ContactUpdateView(PublishedStudyMixin, _ContactUpdateView):
    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pseudonym=self.kwargs['slug'])

        contact_pseudonym = resolve_pseudonym(
            self.study.domain,
            participation_request.pseudonym,
            Contact.domain)
        contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        return contact

    def get_success_url(self):
        return reverse('recruitment:contact',
                       args=[self.kwargs['study_pk'], self.kwargs['slug'], self.kwargs['path']])

    def get_cancel_url(self):
        return self.get_success_url()


class ContactStudiesView(PermissionRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact_studies.html'
    permission_required = 'recruitment.view_participationrequest'

    def get_studies(self, attributeset):
        qs = AttributeSet.objects.filter(pk=attributeset.pk)
        for study in Study.objects.filter(published=True):
            if qs.filter(get_study_filter_q(study)).exists():
                pseudonym = resolve_pseudonym(
                    AttributeSet.domain, attributeset.pseudonym, study.domain)
                request = ParticipationRequest.objects.filter(study=study, pseudonym=pseudonym)
                if not request.exists():
                    yield study, pseudonym

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        attributeset_pseudonym = resolve_pseudonym(
            Contact.domain, self.object.pseudonym, AttributeSet.domain)
        try:
            attributeset = AttributeSet.objects.get(pseudonym=attributeset_pseudonym)
        except AttributeSet.DoesNotExist:
            attributeset = None
        data['attributeset'] = attributeset

        if attributeset:
            data['studies'] = list(self.get_studies(attributeset))

        return data
