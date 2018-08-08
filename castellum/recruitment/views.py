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
import random

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import View

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.studies.models import Study

from . import forms
from .models import AttributeSet
from .models import Participation
from .models import SubjectFilter

monitoring_logger = logging.getLogger('monitoring.contact_data')


class PublishedStudyMixin:
    def dispatch(self, request, *args, **kwargs):
        study_pk = self.kwargs.get('study_pk')
        self.study = get_object_or_404(Study, pk=study_pk)
        if not self.study.published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class RecruitmentView(LoginRequiredMixin, PublishedStudyMixin, ListView):
    model = AttributeSet
    context_object_name = 'attributesets'
    template_name = 'recruitment/recruitment.html'

    def qs_sample(self, qs, k):
        all_ids = list(qs.values_list('id', flat=True))
        if len(all_ids) > k:
            picked_ids = random.sample(all_ids, k)
            return qs.filter(id__in=picked_ids)
        else:
            return qs

    def get_queryset(self, queryset=None):
        qs = AttributeSet.apply_study_filter(self.study, queryset=queryset)
        return self.qs_sample(qs, 6)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['study'] = self.study
        return context


class ContactView(LoginRequiredMixin, PublishedStudyMixin, UpdateView):
    model = Participation
    fields = ['status']
    template_name = 'recruitment/contact.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        self.attributeset = get_object_or_404(
            AttributeSet, pseudonym=self.kwargs['attributeset_slug'])

        contact_pseudonym = resolve_pseudonym(
            settings.DOMAINS['attributeset'],
            self.attributeset.pseudonym,
            settings.DOMAINS['contact'])
        self.contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        pseudonym = resolve_pseudonym(
            settings.DOMAINS['contact'], self.contact.pseudonym, self.study.domain)
        participation, __ = queryset.get_or_create(study=self.study, pseudonym=pseudonym)
        return participation

    def get_success_url(self):
        return reverse('recruitment:select_contact', args=[self.object.study.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        context['contact'] = self.contact
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.updated_at = timezone.now()
        result = super(ContactView, self).form_valid(form)

        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        return result


class AttributeSetDetailView(LoginRequiredMixin, DetailView):
    model = AttributeSet

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        attributeset, __ = queryset.get_or_create(pseudonym=self.kwargs['slug'])
        return attributeset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact_pseudonym'] = resolve_pseudonym(
            settings.DOMAINS['attributeset'], self.object.pseudonym, settings.DOMAINS['contact'])
        return context


class AttributeSetUpdateView(LoginRequiredMixin, UpdateView):
    model = AttributeSet
    fields = '__all__'
    slug_field = 'pseudonym'

    def form_valid(self, form):
        result = super().form_valid(form)
        monitoring_logger.info('ContactData update: {}:{} by {}'.format(
            settings.DOMAINS['attributeset'],
            self.object.pseudonym,
            self.request.user.pk))
        return result


class SubjectFilterView(LoginRequiredMixin, View):
    template_name = "recruitment/filters.html"

    def get_subject_count(self, study):
        return AttributeSet.apply_study_filter(study).count()

    def get_total_count(self):
        return AttributeSet.objects.count()

    def get(self, request, study_pk):
        study = get_object_or_404(Study, pk=study_pk)
        filters = study.subjectfilter_set.all()
        context = {
            "count": self.get_subject_count(study),
            "total_count": self.get_total_count(),
            "study": study,
            "filters": filters,
            "selected_field": "",
            "select_attribute_form": forms.SelectAttributeForm,
            "add_subject_filter_form": None,
        }
        return render(request, self.template_name, context)

    def post(self, request, study_pk):
        study = get_object_or_404(Study, pk=study_pk)
        filters = study.subjectfilter_set.all()

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
                SubjectFilter.objects.create(
                    study_id=study.pk,
                    field_name=selected_field,
                    operator=add_subject_filter_form.cleaned_data["operator"],
                    value=add_subject_filter_form.cleaned_data["value"]
                )
                add_subject_filter_form = None

        context = {
            "count": self.get_subject_count(study),
            "total_count": self.get_total_count(),
            "study": study,
            "filters": filters,
            "selected_field": selected_field,
            "select_attribute_form": select_attribute_form,
            "add_subject_filter_form": add_subject_filter_form,
        }
        return render(request, self.template_name, context)


class RemoveSubjectFilterView(LoginRequiredMixin, PublishedStudyMixin, View):
    def post(self, request, study_pk, filter_id):
        SubjectFilter.objects.get(pk=filter_id).delete()
        return redirect(reverse('recruitment:subject_filter', kwargs={"study_pk": study_pk}))
