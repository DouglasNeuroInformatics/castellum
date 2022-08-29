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

import logging

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.castellum_auth.models import User

from ..forms import MemberForm
from ..forms import MultiMemberForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership

monitoring_logger = logging.getLogger('monitoring.studies')


class StudyMembersView(StudyMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'
    is_filter_trial = False
    tab = 'members'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membership_forms'] = [
            MemberForm(instance=membership) for membership in self.study.studymembership_set.all()
        ]
        return context

    def get_form(self):
        kwargs = self.get_form_kwargs()

        if 'membership' in self.request.POST:
            kwargs['instance'] = get_object_or_404(
                self.study.studymembership_set, pk=self.request.POST['membership']
            )

            form = MemberForm(**kwargs)
        else:
            form = MultiMemberForm(**kwargs)
            form.instance.study = self.object
            form.fields['users'].choices = [
                (user.pk, str(user))
                for user in User.objects.exclude(pk__in=self.object.members.all())
            ]

        return form

    def form_valid(self, form):
        form.instance.study = self.object

        # user has been added to study
        if 'users' in self.request.POST:
            text = 'User {} added user {} to study {}'.format(
                self.request.user.pk, self.request.POST['users'], self.object,
            )
            if 'groups' in self.request.POST:
                text += ' in groups {}'.format(self.request.POST.getlist('groups'))
            monitoring_logger.info(text)

        # user was already a member of study but groups have changed
        elif 'membership' in self.request.POST:
            membership = StudyMembership.objects.get(pk=self.request.POST['membership'])
            old_groups = list(membership.groups.all().values_list('pk', flat=True))
            new_groups = [int(group) for group in self.request.POST.getlist('groups')]
            if old_groups != new_groups:
                monitoring_logger.info(
                    'User {} changed groups of user {} in study {}. Groups: {}'.format(
                        self.request.user.pk,
                        membership.user.pk,
                        self.object,
                        new_groups,
                    )
                )

        form.save()
        return redirect('studies:members', self.object.pk)


class StudyMembershipRemoveView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = StudyMembership
    permission_required = 'studies.change_study'
    is_filter_trial = False
    tab = 'members'

    def get_object(self):
        return get_object_or_404(StudyMembership, pk=self.kwargs['pk'], study=self.study)

    def delete(self, request, *args, **kwargs):
        membership = self.get_object()

        if membership.user.pk == request.user.pk:
            return HttpResponseBadRequest()

        monitoring_logger.info(
            'User {} removed user {} from study {}'.format(
                self.request.user.pk, membership.user.pk, membership.study,
            )
        )

        membership.delete()
        return redirect('studies:members', membership.study.pk)
