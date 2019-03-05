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


from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DetailView

from castellum.contacts.mixins import SubjectMixin
from castellum.contacts.models import Contact
from castellum.contacts.views import ContactUpdateView as _ContactUpdateView
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.studies.models import Study

from .mixins import StudyPermissionMixin
from ..models import AttributeSet
from ..models import ParticipationRequest
from ..utils import get_study_filter_q


class ContactUpdateView(StudyPermissionMixin, _ContactUpdateView):

    def dispatch(self, request, *args, **kwargs):
        self.study = Study.get_by_pk_or_404(self.kwargs.get('study_pk'))
        self.study.raise_404_error_if_study_is_not_published()
        return super().dispatch(request, *args, **kwargs)

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
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['slug']])

    def get_cancel_url(self):
        return self.get_success_url()


class ContactStudiesView(SubjectMixin, LoginRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact_studies.html'

    def get_studies(self, attributeset):
        qs = AttributeSet.objects.filter(pk=attributeset.pk)
        for study in Study.objects.filter(published=True):
            if (
                self.request.user.has_perm('recruitment.add_participationrequest', obj=study) and
                self.request.user.has_perm('studies.access_study', obj=study) and
                qs.filter(get_study_filter_q(study)).exists()
            ):
                request = attributeset.subject.participationrequest_set.filter(study=study)
                if not request.exists():
                    yield study

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        subject = get_subject(Contact.domain, self.object.pseudonym)

        try:
            data['attributeset'] = subject.attributeset
            data['studies'] = list(self.get_studies(subject.attributeset))
        except AttributeSet.DoesNotExist:
            pass

        return data

    def post(self, request, *args, **kwargs):
        study = get_object_or_404(Study, pk=request.POST['study'], published=True)

        for perm in ['recruitment.add_participationrequest', 'studies.access_study']:
            if not request.user.has_perm(perm, obj=study):
                raise PermissionDenied

        subject = get_subject(study.domain, request.POST['pseudonym'])
        pseudonym = resolve_pseudonym(Contact.domain, self.object.pseudonym, study.domain)

        participation_request = ParticipationRequest.objects.create(
            pseudonym=pseudonym, subject=subject, study=study)

        url = reverse('recruitment:contact', args=[study.pk, participation_request.pseudonym])
        return redirect(url + '?contacts')
