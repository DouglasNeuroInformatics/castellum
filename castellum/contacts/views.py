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
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

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


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class ContactUpdateView(LoginRequiredMixin, View):
    template_name = 'contacts/contact_form.html'

    def get(self, request, slug):
        contact = get_object_or_404(Contact, pseudonym=slug)
        context = {
            'availabilities': self.get_availabilities(contact),
            'form': ContactForm(instance=contact),
        }
        return render(request, self.template_name, context)

    def get_availabilities(self, contact):
        weekday = dict.fromkeys(range(6, 21), False)
        availabilities = dict([(i, weekday.copy()) for i in range(5)])

        qs = (Availability.objects.filter(contact=contact)
                                  .order_by("weekday", "hour")
                                  .values_list("weekday", "hour"))

        for weekday, hour in qs:
            availabilities[weekday][hour] = True
        return availabilities

    def post(self, request, slug):
        contact = get_object_or_404(Contact, pseudonym=slug)
        form = ContactForm(data=request.POST, instance=contact)
        if form.is_valid():
            form.save()
            self.save_availability(request.POST, contact)
            msg = 'ContactData update: {}:{} by {}'.format(settings.DOMAINS['contact'], slug,
                                                           self.request.user.pk)
            monitoring_logger.info(msg)
            return redirect(contact.get_absolute_url())
        else:
            return render(request, self.template_name, {'form': form})

    def save_availability(self, post_data, contact):
        self.delete_availability_items(contact)

        availabilities = []
        for weekday in range(5):
            for hour in post_data.getlist("weekday-{}".format(weekday), []):
                availabilities.append(Availability(contact=contact, weekday=weekday, hour=hour))
        Availability.objects.bulk_create(availabilities)

    def delete_availability_items(self, contact):
        Availability.objects.filter(contact=contact).delete()
