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


from django.shortcuts import get_object_or_404
from django.urls import reverse

from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.studies.mixins import StudyPermissionMixin
from castellum.studies.models import Study

from ..models import ParticipationRequest


class ContactUpdateView(StudyPermissionMixin, BaseContactUpdateView):

    def dispatch(self, request, *args, **kwargs):
        self.study = Study.get_by_pk_or_404(self.kwargs.get('study_pk'))
        self.study.raise_404_error_if_study_is_not_published()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pk=self.kwargs['pk'])

        contact_pseudonym = get_pseudonym(participation_request.subject, Contact.domain)
        contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        return contact

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['pk']])
