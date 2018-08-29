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

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.pseudonyms.helpers import resolve_pseudonym

from .forms import ContactForm
from .models import Availability
from .models import Contact

monitoring_logger = logging.getLogger('monitoring.contact_data')


class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    paginate_by = 20


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attributeset_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['contact'], self.object.pseudonym, settings.DOMAINS['attributeset'])
        return context


def save_availability(post_data, contact):
    Availability.objects.filter(contact=contact).delete()

    availabilities = []
    for weekday in range(5):
        for hour in post_data.getlist("weekday-{}".format(weekday), []):
            availabilities.append(Availability(contact=contact, weekday=weekday, hour=hour))
    Availability.objects.bulk_create(availabilities)


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['availabilities'] = {i: {j: False for j in range(6, 21)} for i in range(5)}
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        save_availability(self.request.POST, self.object)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    slug_field = 'pseudonym'

    def get_cancel_url(self):
        return reverse('contacts:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['availabilities'] = self.object.get_availabilities()
        return context

    def form_valid(self, form):
        result = super().form_valid(form)
        save_availability(self.request.POST, self.object)
        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result
