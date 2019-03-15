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
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import list_pseudonyms
from castellum.pseudonyms.registry import subject_data_models
from castellum.utils.views import GetFormView

from .forms import ContactForm
from .forms import SearchForm
from .mixins import SubjectMixin
from .models import Contact

monitoring_logger = logging.getLogger('monitoring.contacts')


class ContactSearchView(PermissionRequiredMixin, GetFormView):
    template_name = 'contacts/contact_search.html'
    permission_required = 'contacts.add_contact'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_number_subjects'] = Contact.objects.count()
        return context

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: {{first_name: "{first_name}"; last_name: "{last_name}"; '
            'date_of_birth: "{date_of_birth}"}} by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        matches = [
            (contact, self.request.user.has_privacy_level(contact.privacy_level))
            for contact in Contact.objects.fuzzy_filter(**form.cleaned_data)
        ]

        return self.render_to_response(self.get_context_data(
            form=form, query='?' + urlencode(form.cleaned_data), matches=matches))


class ContactDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Contact
    slug_field = 'pseudonym'
    permission_required = 'contacts.view_contact'


class ContactCreateView(PermissionRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'contacts.add_contact'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_cancel_url(self):
        return reverse('contacts:search') + '?' + self.request.META['QUERY_STRING']

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_cancel_url(self):
        return reverse('contacts:detail', args=[self.object.pseudonym])

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            Contact.domain,
            self.object.pseudonym,
            self.request.user.pk))
        return result


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
