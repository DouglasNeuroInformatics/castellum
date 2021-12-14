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

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.castellum_auth.models import User

from ..forms import MemberForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership


class StudyMembersView(StudyMixin, PermissionRequiredMixin, SingleObjectMixin, FormView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    is_filter_trial = False
    tab = 'members'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unprivileged_users'] = list(self.get_unprivileged_members())
        return context

    def get_form(self):
        choices = [(None, '---')]
        choices.extend([
            (user.pk, str(user)) for user in User.objects.exclude(pk__in=self.object.members.all())
        ])

        form = MemberForm(**self.get_form_kwargs())
        form.fields['user'].choices = choices
        return form

    def form_valid(self, form):
        form.instance.study = self.object
        form.save()
        return redirect('studies:members', self.object.pk)

    def get_unprivileged_members(self):
        max_privacy_level = self.object.get_filter_max_privacy_level()

        for user in self.object.members.all():
            if user.has_perm('studies.change_study', obj=self.object):
                if user.get_privacy_level() < max_privacy_level:
                    yield user.get_full_name()


class StudyMembershipRemoveView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = StudyMembership
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    is_filter_trial = False
    tab = 'members'

    def get_object(self):
        return get_object_or_404(StudyMembership, pk=self.kwargs['pk'], study=self.study)

    def delete(self, request, *args, **kwargs):
        membership = self.get_object()

        if membership.user.pk == request.user.pk:
            return HttpResponseBadRequest()

        membership.delete()
        return redirect('studies:members', membership.study.pk)
