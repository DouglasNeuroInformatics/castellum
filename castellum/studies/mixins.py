# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from .models import Study
from .models import StudyLock


class StudyMixin:
    """Use this on every view that belongs to a study.

    -   set ``self.study``
    -   check ``access_study`` permission (basically allow access only
        to study members)
    -   check that status is in ``study_status``, otherwise return 404
    -   use study as permission object

    Requires PermissionRequiredMixin.
    """

    study_status = []
    require_member = True

    def get_study(self):
        qs = Study.objects.all()
        if self.study_status:
            qs = qs.filter(status__in=self.study_status)
        key = 'study_pk' if 'study_pk' in self.kwargs else 'pk'
        return get_object_or_404(qs, pk=self.kwargs.get(key))

    def check_auth_conditions(self):
        # establish study context *before* checking permissions
        self.study = self.get_study()
        return super().check_auth_conditions()

    def get_permission_object(self):
        return self.study

    def get_permission_required(self):
        permission_required = set(super().get_permission_required())
        if self.require_member:
            permission_required.add('studies.access_study')
        return permission_required

    def get_object(self):
        if self.model is Study:
            return self.study
        return super().get_object()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['study'] = self.study
        return context


def with_study_lock(fn):
    """Prevent concurrent recruitment.

    This is especially important for mail recruitment, because:

    -   Sending mails is slow, so races are more likely.
    -   Sending mails is a side effect that exists outside of the
        database, so it is not covered by database integrity guarantees.
    -   If we send out mails to subjects and then do not create
        participations for them, we might end up sending mails to the
        same subjects again.
    """

    @functools.wraps(fn)
    def locked(self, *args, **kwargs):
        try:
            lock = StudyLock.objects.create(study=self.study)
        except IntegrityError:
            messages.error(self.request, _(
                'Another recruitment action is currently in progress. '
                'Please try again later.'
            ))
            return self.get(self.request, **self.kwargs)

        try:
            return fn(self, *args, **kwargs)
        finally:
            lock.delete()

    return locked
