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
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from castellum.pseudonyms.helpers import resolve_pseudonym

from .forms import ContactForm
from .forms import PreludeForm
from .models import Contact
from .models import TimeSlot

monitoring_logger = logging.getLogger('monitoring.contact_data')


class ContactIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'contacts/contact_index.html'


class ContactSearchView(LoginRequiredMixin, ListView):
    model = Contact
    paginate_by = 20


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['attributeset_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['contact'], self.object.pseudonym, settings.DOMAINS['attributeset'])

        timeslots = TimeSlot.objects.all()
        days = [
            self.object.availability_monday.all(),
            self.object.availability_tuesday.all(),
            self.object.availability_wednesday.all(),
            self.object.availability_thursday.all(),
            self.object.availability_friday.all(),
        ]
        context['availability'] = [
            [(timeslot.hour, timeslot in day) for timeslot in timeslots] for day in days]

        return context


class ContactCreatePreludeView(LoginRequiredMixin, FormView):
    form_class = PreludeForm
    template_name = 'contacts/contact_create_prelude.html'

    def form_valid(self, form):
        url = reverse('contacts:create-matches') + '?' + urlencode(form.cleaned_data)
        return redirect(url)


class ContactCreateMatchesView(LoginRequiredMixin, View):
    template_name = 'contacts/contact_create_matches.html'

    def get(self, request, *args, **kwargs):
        form = PreludeForm(request.GET)
        if not form.is_valid():
            return HttpResponseBadRequest()

        query = '?' + urlencode(form.cleaned_data)
        matches = Contact.objects.filter(**form.cleaned_data).all()

        if matches:
            return render(self.request, self.template_name, context={
                'query': query,
                'object_list': matches,
            })
        else:
            url = reverse('contacts:create-form') + query
            return redirect(url)


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm

    def get_cancel_url(self):
        if self.request.GET.get('matches'):
            return reverse('contacts:create-matches') + '?' + self.request.META['QUERY_STRING']
        return reverse('contacts:index')

    def get_initial(self):
        initial = super().get_initial()
        for key in ['first_name', 'last_name', 'birthday']:
            if key in self.request.GET:
                initial[key] = self.request.GET[key]
        return initial

    def form_valid(self, form):
        result = super().form_valid(form)
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
        if self.request.GET.get('matches'):
            return reverse('contacts:create-matches') + '?' + self.request.META['QUERY_STRING']
        return reverse('contacts:index')

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            settings.DOMAINS['contact'],
            self.object.pseudonym,
            self.request.user.pk))
        return result
