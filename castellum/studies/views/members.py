# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging

from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_noop
from django.views.generic import DeleteView
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin

from castellum.audit.helpers import audit
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.castellum_auth.models import User

from ..forms import MemberForm
from ..forms import MultiMemberForm
from ..mixins import StudyMixin
from ..models import Study
from ..models import StudyMembership

monitoring_logger = logging.getLogger('monitoring.studies')


class StudyMembersView(
    StudyMixin, PermissionRequiredMixin, SingleObjectMixin, FormView
):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_members.html'
    permission_required = 'studies.change_study'
    tab = 'members'

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membership_forms'] = [
            MemberForm(instance=membership)
            for membership in self.study.studymembership_set.all()
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

        def format_list(a):
            return [int(pk) for pk in sorted(a)]

        if 'membership' in self.request.POST:
            membership = StudyMembership.objects.get(pk=self.request.POST['membership'])
            old_groups = set(membership.groups.values_list('pk', flat=True))
            new_groups = {int(group) for group in self.request.POST.getlist('groups')}
            if old_groups != new_groups:
                monitoring_logger.info(
                    f'Membership changed: study {self.study.pk} '
                    f'user {membership.user.pk} groups {format_list(new_groups)} '
                    f'by {self.request.user.pk}'
                )
                audit(
                    gettext_noop('member changed'),
                    self.request.user.username,
                    study_pk=self.study.pk,
                    extra={
                        'member': membership.user.username,
                        'groups': format_list(new_groups),
                    },
                )
        else:
            monitoring_logger.info(
                'Membership created: study {} users {} groups {} by {}'.format(
                    self.study.pk,
                    format_list(self.request.POST.getlist('users')),
                    format_list(self.request.POST.getlist('groups')),
                    self.request.user.pk,
                )
            )
            for member in form.cleaned_data['users']:
                audit(
                    gettext_noop('member added'),
                    self.request.user.username,
                    study_pk=self.study.pk,
                    extra={
                        'member': member.username,
                        'groups': format_list(self.request.POST.getlist('groups')),
                    },
                )

        form.save()
        return redirect('studies:members', self.object.pk)


class StudyMembershipRemoveView(StudyMixin, PermissionRequiredMixin, DeleteView):
    model = StudyMembership
    permission_required = 'studies.change_study'
    tab = 'members'

    def get_object(self):
        return get_object_or_404(
            StudyMembership, pk=self.kwargs['pk'], study=self.study
        )

    def get_success_url(self):
        return reverse('studies:members', args=[self.study.pk])

    def form_valid(self, form):
        if self.object.user.pk == self.request.user.pk:
            return HttpResponseBadRequest()

        monitoring_logger.info(
            f'Membership removed: study {self.object.study.pk} '
            f'user {self.object.user.pk} by {self.request.user.pk}'
        )
        audit(
            gettext_noop('member removed'),
            self.request.user.username,
            study_pk=self.study.pk,
            extra={'member': self.object.user.username},
        )

        return super().form_valid(form)
