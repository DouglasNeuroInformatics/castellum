# (c) 2018-2022 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.utils.mail import MailContext

from .forms import AdditionalInfoForm
from .forms import DataProtectionForm
from .models import Consent
from .models import ConsentDocument
from .models import Subject


class SubjectMixin:
    """Use this on every view that represents a subject.

    Requires ``AccessMixin``.

    -   set ``self.subject``
    -   check privacy level
    """

    def get_subject(self):
        obj = self.get_object()
        if isinstance(obj, Subject):
            return obj
        else:
            return obj.subject

    def check_auth_conditions(self):
        if not super().check_auth_conditions():
            return False
        self.subject = self.get_subject()
        return self.request.user.has_privacy_level(self.subject.privacy_level)

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
        if settings.CASTELLUM_GDPR_NOTIFICATION_TO:
            old = Subject.objects.get(pk=self.object.pk)

            with MailContext('internal') as ctx:
                if self.object.export_requested and not old.export_requested:
                    rel = reverse('subjects:detail', args=[self.object.uuid])
                    url = self.request.build_absolute_uri(rel)

                    self.object.to_be_deleted_notified = ctx.send_mail(
                        settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_SUBJECT,
                        (
                            lambda: {'url': url},
                            settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY,
                            settings.CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY_EN,
                        ),
                        settings.CASTELLUM_GDPR_NOTIFICATION_TO,
                    )

                if self.object.to_be_deleted and not self.object.to_be_deleted_notified:
                    rel = reverse('subjects:detail', args=[self.object.uuid])
                    url = self.request.build_absolute_uri(rel)

                    self.object.to_be_deleted_notified = ctx.send_mail(
                        settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT,
                        (
                            lambda: {'url': url},
                            settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY,
                            settings.CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY_EN,
                        ),
                        settings.CASTELLUM_GDPR_NOTIFICATION_TO,
                    )

            # If a user explicitly removes the ``to_be_deleted`` they
            # expect that this task is done. If there are still reasons
            # for deletion there should be a new notificaition.
            if not self.object.to_be_deleted and self.object.to_be_deleted_notified:
                old = Subject.objects.get(pk=self.object.pk)
                if old.to_be_deleted:
                    self.object.to_be_deleted_notified = False

        return super().form_valid(form)


class BaseConsentChangeView(PermissionRequiredMixin, CreateView):
    model = Consent
    fields = ['document']
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/subject_consent_form.html'

    def get_object(self):
        # weird because model = Consent, but this is only used in
        # SubjectMixin, not in CreateView
        return get_object_or_404(Subject, uuid=self.kwargs['uuid'])

    def get_form(self):
        if not ConsentDocument.objects.exists():
            ConsentDocument.objects.create()
        return super().get_form()

    def form_valid(self, form):
        Consent.objects.filter(subject=self.subject).delete()
        form.instance.subject = self.subject
        return super().form_valid(form)


class BaseAdditionalInfoUpdateView(PermissionRequiredMixin, UpdateView):
    model = Subject
    form_class = AdditionalInfoForm
    permission_required = 'subjects.change_subject'
    template_name = 'subjects/subject_additional_info_form.html'
