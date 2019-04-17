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

from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.models import Subject

from .forms import ContactForm
from .models import Contact

monitoring_logger = logging.getLogger('monitoring.contacts')


class SubjectMixin:
    @cached_property
    def subject(self):
        obj = self.get_object()
        if isinstance(obj, Subject):
            return obj
        else:
            return obj.subject

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.has_privacy_level(self.subject.privacy_level):
                raise PermissionDenied(_('Insufficient privacy level'))
        return super().dispatch(request, *args, **kwargs)


class BaseContactUpdateView(SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'contacts.change_contact'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_cancel_url(self):
        return self.get_success_url()

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result
