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
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from .models import Subject
from .models import SubjectNote


class SubjectMixin:
    @cached_property
    def subject(self):
        obj = self.get_object()
        if isinstance(obj, Subject):
            return obj
        else:
            return obj.subject

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if not request.user.has_privacy_level(self.subject.privacy_level):
                raise PermissionDenied(_('Insufficient privacy level'))
        return super().dispatch(request, *args, **kwargs)


class BaseSubjectUpdateView(SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = Subject
    fields = '__all__'
    permission_required = 'subjects.change_subject'

    def get_notes_form(self):
        form_class = forms.modelform_factory(SubjectNote, fields=('content',))
        return form_class(prefix='{prefix}')

    def get_notes_formset(self):
        formset_class = forms.modelformset_factory(SubjectNote, fields=('content',),
                                                   extra=0, can_delete=True)
        kwargs = self.get_form_kwargs()
        kwargs.pop('instance')
        kwargs.pop('initial')
        return formset_class(queryset=SubjectNote.objects.filter(subject=self.object), **kwargs)

    def get_context_data(self, **kwargs):
        if 'notes_formset' not in kwargs:
            kwargs['notes_formset'] = self.get_notes_formset()
        kwargs["template_form"] = self.get_notes_form()

        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        notes_formset = self.get_notes_formset()

        if form.is_valid() and notes_formset.is_valid():
            return self.form_valid(form, notes_formset)
        else:
            return self.form_invalid(form, notes_formset)

    def form_invalid(self, form, session_formset):
        return self.render_to_response(
            self.get_context_data(form=form, session_formset=session_formset)
        )

    def form_valid(self, form, contactnote_formset):

        response = super().form_valid(form)

        for subform in contactnote_formset:
            subform.instance.subject = self.object
        contactnote_formset.save()

        return response
