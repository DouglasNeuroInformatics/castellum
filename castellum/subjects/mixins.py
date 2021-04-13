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

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.utils.mail import MailContext

from .forms import AdditionalInfoForm
from .forms import DataProtectionForm
from .models import Subject


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

            with MailContext('internal') as ctx:
                if self.object.export_requested and not old.export_requested:
                    rel = reverse('subjects:detail', args=[self.object.slug])
                    url = self.request.build_absolute_uri(rel)

                    self.object.to_be_deleted_notified = ctx.send_mail(
                        settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_SUBJECT,
                        (
                            lambda: {'url': url},
                            settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY,
                        [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
                    )

                if self.object.to_be_deleted and not self.object.to_be_deleted_notified:
                    rel = reverse('subjects:detail', args=[self.object.slug])
                    url = self.request.build_absolute_uri(rel)

                    self.object.to_be_deleted_notified = ctx.send_mail(
                        settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT,
                        (
                            lambda: {'url': url},
                            settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY,
                        ),
                        [settings.CASTELLUM_DELETE_NOTIFICATION_TO],
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
    form_class = AdditionalInfoForm
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/subject_additional_info_form.html'
