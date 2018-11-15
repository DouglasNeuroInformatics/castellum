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

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import BaseModelFormSet
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import View

from extra_views import ModelFormSetView

from castellum.settings import CASTELLUM_EXPECTED_SUBJECT_FACTOR
from castellum.studies.models import Study

from .. import forms
from ..models import AttributeSet
from ..models import SubjectFilter
from ..models import SubjectFilterGroup
from .mixins import UnpublishedStudyMixin


class FilterGroupListView(LoginRequiredMixin, ListView):
    model = SubjectFilterGroup
    template_name = 'recruitment/filtergroup_list.html'

    def dispatch(self, *args, **kwargs):
        self.study = get_object_or_404(Study, pk=self.kwargs['study_pk'])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        context['total_count'] = AttributeSet.apply_study_filter(self.study).count()
        return context

    def get(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.object_list = self.get_queryset()
            context = self.get_context_data()

            if self.study.min_subjects_count == 0:
                messages.error(self.request, _(
                    'Weak recruitment process. '
                    'The number of subjects is not defined for this study.'))
            elif context['total_count'] < self.study.min_subjects_count\
                    * CASTELLUM_EXPECTED_SUBJECT_FACTOR:
                        messages.error(self.request, _(
                            'The number of potential subjects is probably '
                            'not sufficient for this study.'))

            return self.render_to_response(context)

        else:
            group = SubjectFilterGroup.objects.create(study=self.study)
            return redirect(group.get_absolute_url())


class FilterGroupCreateView(LoginRequiredMixin, UnpublishedStudyMixin, View):
    def post(self, *args, **kwargs):
        group = SubjectFilterGroup.objects.create(study=self.study)
        return redirect(group.get_absolute_url())


class FilterGroupDeleteView(LoginRequiredMixin, UnpublishedStudyMixin, DeleteView):
    model = SubjectFilterGroup
    template_name = 'recruitment/filtergroup_confirm_delete.html'

    def get_context_data(self, **kwargs):
        if self.study != self.object.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        return data

    def get_success_url(self):
        return reverse('recruitment:filtergroup_index', args=[self.study.pk])


class FilterFormSet(BaseModelFormSet):

    def clean(self):

        super().clean()

        values = []
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                values.append((
                    form.cleaned_data.get('field_name'),
                    form.cleaned_data.get('operator'),
                    form.cleaned_data.get('value'),
                ))

        if len(set(values)) != len(values):
            raise ValidationError(_('There are duplicates in filters. Please change or '
                                    'delete filter!'))


class FilterGroupUpdateView(LoginRequiredMixin, UnpublishedStudyMixin, ModelFormSetView):
    model = SubjectFilter
    form_class = forms.SubjectFilterForm
    formset_class = FilterFormSet
    factory_kwargs = {
        'can_delete': True,
    }
    template_name = "recruitment/filtergroup.html"

    def dispatch(self, *args, **kwargs):
        self.group = get_object_or_404(SubjectFilterGroup, pk=self.kwargs['pk'])
        return super().dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.filter(group=self.group)

    def get_context_data(self, **kwargs):
        if self.study != self.group.study:
            raise Http404

        data = super().get_context_data(**kwargs)
        data['study'] = self.study
        data['group'] = self.group
        data['total_count'] = AttributeSet.objects.count()
        return data


class FilterGroupDuplicateView(LoginRequiredMixin, View):
    def post(self, request, study_pk, pk):
        study = get_object_or_404(Study, pk=study_pk)
        if study.published:
            raise PermissionDenied
        original = get_object_or_404(SubjectFilterGroup, study=study, pk=pk)
        SubjectFilterGroup.objects.clone(original)
        messages.success(request, _(
            'The filters have been duplicated. You can now edit the duplicate.'))
        return redirect('recruitment:filtergroup_index', study.pk)
