# (c) 2018-2020
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
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.utils.mail import send_mail

from .forms import DataProtectionForm
from .models import Subject
from .models import SubjectNote


class SubjectMixin:
    """Use this on every view that represents a subject.

    -   set ``self.subject``
    -   check privacy level
    """

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
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = self.subject
        return context


class BaseDataProtectionUpdateView(PermissionRequiredMixin, UpdateView):
    model = Subject
    form_class = DataProtectionForm
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/subject_data_protection_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if settings.CASTELLUM_DELETE_NOTIFICATION_TO:
            old = Subject.objects.get(pk=self.object.pk)
            if self.object.export_requested and not old.export_requested:
                rel = reverse('subjects:detail', args=[self.object.pk])
                url = self.request.build_absolute_uri(rel)

                self.object.to_be_deleted_notified = send_mail(
                    settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_SUBJECT,
                    (settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY, {'url': url}),
                    [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
                    context='internal',
                )

            if self.object.to_be_deleted and not self.object.to_be_deleted_notified:
                rel = reverse('subjects:detail', args=[self.object.pk])
                url = self.request.build_absolute_uri(rel)

                self.object.to_be_deleted_notified = send_mail(
                    settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT,
                    (settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY, {'url': url}),
                    [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
                    context='internal',
                )

            # If a user explicitly removes the ``to_be_deleted`` they
            # expect that this task is done. If there are still reasons
            # for deletion there should be a new notificaition.
            if not self.object.to_be_deleted and self.object.to_be_deleted_notified:
                old = Subject.objects.get(pk=self.object.pk)
                if old.to_be_deleted:
                    self.object.to_be_deleted_notified = False

        return super().form_valid(form)


class BaseAdditionalInfoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Subject
    fields = [
        'note_hard_of_hearing',
        'note_difficult_to_understand',
        'note_abusive_language',
        'availability_monday',
        'availability_tuesday',
        'availability_wednesday',
        'availability_thursday',
        'availability_friday',
        'not_available_until',
        'source',
    ]
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/subject_additional_info_form.html'

    def get_notes_form(self):
        form_class = forms.modelform_factory(SubjectNote, fields=['content'])
        return form_class(prefix='{prefix}')

    def get_notes_formset(self):
        formset_class = forms.modelformset_factory(
            SubjectNote, fields=['content'], extra=0, can_delete=True
        )
        kwargs = self.get_form_kwargs()
        kwargs.pop('instance')
        kwargs.pop('initial')
        return formset_class(queryset=SubjectNote.objects.filter(subject=self.object), **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'notes_formset' not in context:
            context['notes_formset'] = self.get_notes_formset()
        context['template_form'] = self.get_notes_form()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        notes_formset = self.get_notes_formset()

        if form.is_valid() and notes_formset.is_valid():
            return self.form_valid(form, notes_formset)
        else:
            return self.form_invalid(form, notes_formset)

    def form_invalid(self, form, notes_formset):
        return self.render_to_response(
            self.get_context_data(form=form, notes_formset=notes_formset)
        )

    def form_valid(self, form, notes_formset):
        response = super().form_valid(form)

        for subform in notes_formset:
            subform.instance.subject = self.object
        notes_formset.save()

        return response
