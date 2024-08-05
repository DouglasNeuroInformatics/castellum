# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
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
    -   check that is_filter_trial has desired value
    -   use study as permission object

    Requires PermissionRequiredMixin.
    """

    study_status = []
    is_filter_trial = None
    require_member = True

    def get_study(self):
        qs = Study.objects.all()
        if self.study_status:
            qs = qs.filter(status__in=self.study_status)
        if self.is_filter_trial is not None:
            qs = qs.filter(is_filter_trial=self.is_filter_trial)
        key = 'study_pk' if 'study_pk' in self.kwargs else 'pk'
        return get_object_or_404(qs, pk=self.kwargs.get(key))

    def check_auth_conditions(self):
        self.study = self.get_study()
        return super().check_auth_conditions()

    def get_permission_object(self):
        return self.study

    def get_permission_required(self):
        permission_required = set(super().get_permission_required())
        if self.require_member:
            permission_required.add('studies.access_study')
        return permission_required

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
