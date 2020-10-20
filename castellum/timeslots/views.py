# (c) 2018-2020
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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView

import requests
from stronghold.decorators import public

from .forms import InvitationForm
from .forms import PollForm
from .models import Invitation
from .models import Poll


class PollFormMixin(LoginRequiredMixin):
    model = Poll
    form_class = PollForm

    def get_success_url(self):
        return reverse('timeslots:poll-update', args=[self.object.pk])

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)


class PollCreateView(PollFormMixin, CreateView):
    pass


class PollUpdateView(PollFormMixin, UpdateView):
    pass


class PollDeleteView(LoginRequiredMixin, DeleteView):
    model = Poll

    def get_success_url(self):
        return reverse('index')


@method_decorator(public, 'dispatch')
class PollJsonView(DetailView):
    model = Poll

    def get(self, request, *args, **kwargs):
        if request.GET.get('token') != settings.TIMESLOT_TOKEN:
            raise PermissionDenied

        self.object = self.get_object()
        return JsonResponse({
            i.pseudonym: i.timeslot.datetime
            for i in self.object.invitation_set.all()
            if i.timeslot
        })


@method_decorator(public, 'dispatch')
class InvitationUpdateView(UpdateView):
    model = Invitation
    slug_field = 'pseudonym'
    slug_url_kwarg = 'pseudonym'
    form_class = InvitationForm

    def get_object(self):
        return get_object_or_404(
            Invitation,
            poll__pk=self.kwargs['poll_pk'],
            pseudonym=self.kwargs['pseudonym'],
        )

    def get_success_url(self):
        return reverse('timeslots:invitation', args=[self.object.poll.pk, self.object.pseudonym])

    def form_valid(self, form, *args):
        messages.success(self.request, _('Your reservation has been saved.'))
        response = super().form_valid(form, *args)
        if settings.TIMESLOTS_PING_URL:
            r = requests.post(settings.TIMESLOTS_PING_URL % self.object.poll.pk)
            r.raise_for_status()
        return response
