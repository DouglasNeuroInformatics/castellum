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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views import generic

from castellum.recruitment.models import AttributeSet

from . import forms
from . import models


class IndexView(LoginRequiredMixin, generic.ListView):
    model = models.Study


class CreateView(LoginRequiredMixin, generic.CreateView):
    model = models.Study
    fields = '__all__'
    success_url = '/'


class SubjectFilterView(LoginRequiredMixin, View):
    template_name = "studies/filters.html"

    def get_subject_count(self, filters):
        filter_dict = {"{}__{}".format(f.field_name, f.operator): f.value for f in filters}
        return AttributeSet.objects.filter(**filter_dict).count()

    def get_filters_for_study(self, study_id):
        return models.SubjectFilter.objects.filter(study__id=study_id)

    def get(self, request, study_id):
        filters = self.get_filters_for_study(study_id)
        context = {
            "count": self.get_subject_count(filters),
            "filters": filters,
            "study_id": study_id,
            "selected_field": "",
            "select_attribute_form": forms.SelectAttributeForm,
            "add_subject_filter_form": None,
        }
        return render(request, self.template_name, context)

    def post(self, request, study_id):
        filters = self.get_filters_for_study(study_id)

        select_attribute_form = forms.SelectAttributeForm(request.POST)
        add_subject_filter_form = forms.AddSubjectFilterForm()

        selected_field = None
        if select_attribute_form.is_valid():
            selected_field = select_attribute_form.cleaned_data["field_name"]

        if selected_field:
            initial_data = {
                "field_name": selected_field,
            }
            add_subject_filter_form = forms.AddSubjectFilterForm(request.POST, initial=initial_data)
            if add_subject_filter_form.is_valid():
                models.SubjectFilter.objects.create(
                    study_id=study_id,
                    field_name=selected_field,
                    field_type="text",
                    operator=add_subject_filter_form.cleaned_data["operator"],
                    value=add_subject_filter_form.cleaned_data["value"]
                )
                add_subject_filter_form = None

        context = {
            "count": self.get_subject_count(filters),
            "filters": filters,
            "study_id": study_id,
            "selected_field": selected_field,
            "select_attribute_form": select_attribute_form,
            "add_subject_filter_form": add_subject_filter_form,
        }
        return render(request, self.template_name, context)


class RemoveSubjectFilterView(LoginRequiredMixin, View):
    def post(self, request, study_id, filter_id):
        models.SubjectFilter.objects.get(pk=filter_id).delete()
        return redirect(reverse('studies:subject_filter', kwargs={"study_id": study_id}))
