# SPDX-FileCopyrightText: 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_noop
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import UpdateView

from castellum.audit.helpers import audit
from castellum.castellum_auth.mixins import PermissionRequiredMixin

from .forms import ContactForm
from .models import Contact


@method_decorator(sensitive_post_parameters(), 'dispatch')
class BaseContactUpdateView(PermissionRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    permission_required = 'subjects.change_subject'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        audit(
            gettext_noop('subject updated'),
            self.request.user.username,
            subject_pk=self.object.subject_uuid,
        )
        return super().form_valid(form)
