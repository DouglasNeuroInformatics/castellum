# (c) 2018-2021
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

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import ReadonlyFormMixin
from .forms import ReadonlyModelForm


class ReadonlyMixin:
    def get_readonly(self):
        raise NotImplementedError

    def get_form_class(self):
        if self.form_class:
            if issubclass(self.form_class, ReadonlyFormMixin):
                return self.form_class
            else:
                raise ImproperlyConfigured('form_class is not a subclass of ReadonlyFormMixin')
        return forms.modelform_factory(self.model, fields=self.fields, form=ReadonlyModelForm)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly'] = self.get_readonly()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['readonly'] = self.get_readonly()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.get_readonly():
            return HttpResponseBadRequest()
        return super().post(request, *args, **kwargs)


def get_next_url(request, default='/'):
    url = request.POST.get('next', request.GET.get('next'))
    is_safe = url_has_allowed_host_and_scheme(
        url, allowed_hosts=[request.get_host()], require_https=request.is_secure()
    )
    if url and is_safe:
        return url
    else:
        return default
