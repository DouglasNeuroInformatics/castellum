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
            'form': ContactForm(instance=contact),
        }
        return render(request, self.template_name, context)

    def post(self, request, slug):
        contact = get_object_or_404(Contact, pseudonym=slug)
        form = ContactForm(data=request.POST, instance=contact)
        if form.is_valid():
            form.save()
            msg = 'ContactData update: {}:{} by {}'.format(settings.DOMAINS['contact'], slug,
                                                           self.request.user.pk)
            monitoring_logger.info(msg)
            return redirect(contact.get_absolute_url())
        else:
            return render(request, self.template_name, {'form': form})
