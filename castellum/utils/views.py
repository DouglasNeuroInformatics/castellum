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

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import HttpResponseBadRequest
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin

from .forms import ReadonlyFormMixin
from .forms import ReadonlyModelForm


class GetFormMixin(FormMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.GET:
            kwargs['data'] = self.request.GET
        return kwargs


class GetFormView(GetFormMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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


class SearchMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        q_str = self.request.GET.get('q')
        if q_str:
            for part in q_str.split():
                q = models.Q()
                for field in self.search_fields:
                    q |= models.Q(**{field + '__icontains': part})
                qs = qs.filter(q).distinct()
        return qs
