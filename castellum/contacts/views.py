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

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.subjects.models import Subject
from castellum.utils.views import GetFormView

from .forms import ContactForm
from .forms import SearchForm
from .mixins import SubjectMixin
from .models import Contact

monitoring_logger = logging.getLogger('monitoring.contacts')


class ContactSearchView(PermissionRequiredMixin, GetFormView):
    template_name = 'contacts/contact_search.html'
    permission_required = 'contacts.view_contact'
    form_class = SearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_number_subjects'] = Contact.objects.count()
        return context

    def user_has_privacy_level(self, contact):
        return self.request.user.has_privacy_level(contact.subject.privacy_level)

    def form_valid(self, form):
        monitoring_logger.info((
            'Subject search: {{first_name: "{first_name}"; last_name: "{last_name}"; '
            'date_of_birth: "{date_of_birth}"}} by {user}'
        ).format(user=self.request.user.pk, **form.cleaned_data))

        matches = [
            (contact, self.user_has_privacy_level(contact))
            for contact in Contact.objects.fuzzy_filter(**form.cleaned_data)
        ]

        return self.render_to_response(self.get_context_data(
            form=form, query='?' + urlencode(form.cleaned_data), matches=matches))


class ContactDetailView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    permission_required = 'contacts.view_contact'
    template_name = 'contacts/contact_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pseudonym = get_pseudonym(self.object, Contact.domain)
        context['contact'] = Contact.objects.get(pseudonym=pseudonym)
        return context


class ContactCreateView(PermissionRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'contacts.add_contact'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_cancel_url(self):
        return reverse('contacts:index') + '?' + self.request.META['QUERY_STRING']

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


class ContactUpdateView(BaseContactUpdateView):
    def get_object(self):
        subject = get_object_or_404(Subject, pk=self.kwargs['pk'])
        pseudonym = get_pseudonym(subject, Contact.domain)
        return get_object_or_404(Contact, pseudonym=pseudonym)


class ContactExportView(SubjectMixin, PermissionRequiredMixin, DetailView):
    model = Subject
    template_name = 'contacts/contact_export.html'
    permission_required = 'subjects.view_subject'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        monitoring_logger.info('GDPR-Request export: {} by {}'.format(
            self.object.pk, self.request.user.pk))

        context['dataset_list'] = []

        pseudonym = get_pseudonym(self.object, Contact.domain)
        context['dataset_list'].append(Contact.objects.get(pseudonym=pseudonym))

        try:
            context['dataset_list'].append(self.object.attributeset)
        except ObjectDoesNotExist:
            pass

        for participation in self.object.participationrequest_set.all():
            context['dataset_list'].append(participation)

        return context
