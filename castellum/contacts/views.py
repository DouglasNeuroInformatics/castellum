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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from castellum.pseudonyms.helpers import list_pseudonyms
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.pseudonyms.registry import subject_data_models
from castellum.recruitment.models import AttributeSet

from .forms import ContactForm
from .forms import PreludeForm
from .models import Contact
from .models import TimeSlot

monitoring_logger = logging.getLogger('monitoring.contacts')


class ContactIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'contacts/contact_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_number_subjects'] = Contact.objects.all().count()
        return context


class ContactSearchView(LoginRequiredMixin, ListView):
    model = Contact
    paginate_by = 20


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['attributeset_pseudonym'] = resolve_pseudonym(
            Contact.domain, self.object.pseudonym, AttributeSet.domain)

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


class ContactCreatePreludeView(LoginRequiredMixin, TemplateView):
    template_name = 'contacts/contact_create_prelude.html'

    def get(self, request, *args, **kwargs):
        form_kwargs = {}
        if request.GET:
            form_kwargs['data'] = request.GET
        form = PreludeForm(**form_kwargs)

        if form.is_valid():
            return self.render_to_response({
                'form': form,
                'query': '?' + urlencode(form.cleaned_data),
                'matches': Contact.objects.fuzzy_filter(**form.cleaned_data),
            })
        else:
            return self.render_to_response({
                'form': form,
            })


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm

    def get_cancel_url(self):
        return reverse('contacts:create') + '?' + self.request.META['QUERY_STRING']

    def get_initial(self):
        initial = super().get_initial()
        for key in ['first_name', 'last_name', 'birthday']:
            if key in self.request.GET:
                initial[key] = self.request.GET[key]
        return initial

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    slug_field = 'pseudonym'

    def get_cancel_url(self):
        return reverse('contacts:create') + '?' + self.request.META['QUERY_STRING']

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result


class RequestCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'contacts/subjectexportrequest_form.html'

    def get(self, request, *args, **kwargs):
        form_kwargs = {}
        if request.GET:
            form_kwargs['data'] = request.GET
        form = PreludeForm(**form_kwargs)

        if form.is_valid():
            return self.render_to_response({
                'form': form,
                'matches': Contact.objects.fuzzy_filter(**form.cleaned_data),
            })
        else:
            return self.render_to_response({
                'form': form,
            })


class ContactExportView(LoginRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    template_name = 'contacts/contact_export.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset_list'] = [self.object]

        pseudonyms = list_pseudonyms(Contact.domain, self.object.pseudonym)
        for domain, pseudonym in pseudonyms:
            if domain == Contact.domain:
                continue
            for model in subject_data_models:
                try:
                    instance = model.get_by_pseudonym(domain, pseudonym)
                    context['dataset_list'].append(instance)
                except model.DoesNotExist:
                    continue

        return context
