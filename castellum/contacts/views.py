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

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import list_pseudonyms
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.pseudonyms.registry import subject_data_models
from castellum.recruitment.models import AttributeSet

from .forms import ContactForm
from .forms import PreludeForm
from .mixins import SubjectMixin
from .models import Contact
from .models import TimeSlot

monitoring_logger = logging.getLogger('monitoring.contacts')


class ContactIndexView(PermissionRequiredMixin, TemplateView):
    template_name = 'contacts/contact_index.html'
    permission_required = 'contacts.view_contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_number_subjects'] = Contact.objects.all().count()
        return context


class ContactSearchView(PermissionRequiredMixin, ListView):
    model = Contact
    paginate_by = 20
    permission_required = 'contacts.view_contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        contacts = []
        privacy_level_user = self.request.user.get_privacy_level()
        for contact in context['object_list']:
            can_access = privacy_level_user >= contact.privacy_level
            contacts.append((contact, can_access))
        context['contacts'] = contacts
        return context


class ContactDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    permission_required = 'contacts.view_contact'

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

        weekdays = [
            _("monday"),
            _("tuesday"),
            _("wednesday"),
            _("thursday"),
            _("friday"),
        ]

        context['availability'] = [
            (weekdays[i], [
                (timeslot.hour, timeslot in days[i])
                for timeslot in timeslots
            ]) for i in range(5)]

        return context


class ContactCreatePreludeView(PermissionRequiredMixin, TemplateView):
    template_name = 'contacts/contact_create_prelude.html'
    permission_required = 'contacts.add_contact'

    def get(self, request, *args, **kwargs):
        form_kwargs = {}
        if request.GET:
            form_kwargs['data'] = request.GET
        form = PreludeForm(**form_kwargs)

        if form.is_valid():
            privacy_level_user = request.user.get_privacy_level()
            matches = []
            for contact in Contact.objects.fuzzy_filter(**form.cleaned_data):
                can_access = privacy_level_user >= contact.privacy_level
                matches.append((contact, can_access))

            return self.render_to_response({
                'form': form,
                'query': '?' + urlencode(form.cleaned_data),
                'matches': matches,
            })
        else:
            return self.render_to_response({
                'form': form,
            })


class ContactCreateView(PermissionRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'contacts.add_contact'

    def get_cancel_url(self):
        return reverse('contacts:create') + '?' + self.request.META['QUERY_STRING']

    def get_initial(self):
        initial = super().get_initial()
        for key in ['first_name', 'last_name', 'date_of_birth']:
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


class ContactUpdateView(SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    slug_field = 'pseudonym'
    permission_required = 'contacts.change_contact'

    def get_cancel_url(self):
        if self.request.META['QUERY_STRING']:
            return reverse('contacts:create') + '?' + self.request.META['QUERY_STRING']
        else:
            return reverse('contacts:detail', args=[self.object.pseudonym])

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result


class RequestCreateView(PermissionRequiredMixin, TemplateView):
    template_name = 'contacts/subjectexportrequest_form.html'
    permission_required = 'contacts.view_contact'

    def get(self, request, *args, **kwargs):
        form_kwargs = {}
        if request.GET:
            form_kwargs['data'] = request.GET
        form = PreludeForm(**form_kwargs)

        if form.is_valid():
            monitoring_logger.info((
                'GDPR-Request: {{first_name: "{first_name}"; last_name: "{last_name}"; '
                'date_of_birth: "{date_of_birth}"}} by {user}'
            ).format(user=request.user.pk, **form.cleaned_data))

            privacy_level_user = request.user.get_privacy_level()
            matches = []
            for contact in Contact.objects.fuzzy_filter(**form.cleaned_data):
                can_access = privacy_level_user >= contact.privacy_level
                matches.append((contact, can_access))

            return self.render_to_response({
                'form': form,
                'matches': matches,
            })
        else:
            return self.render_to_response({
                'form': form,
            })


class ContactExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    template_name = 'contacts/contact_export.html'
    permission_required = 'contacts.view_contact'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monitoring_logger.info('GDPR-Request export: {}:{} by {}'.format(
            Contact.domain, self.object.pseudonym, self.request.user.pk))

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
