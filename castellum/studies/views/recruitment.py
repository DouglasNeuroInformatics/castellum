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
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django.views.generic import View

from dateutil.relativedelta import relativedelta

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment import filter_queries
from castellum.recruitment.mixins import BaseMailRecruitmentView
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext

from ..forms import ExcludedStudiesForm
from ..mixins import StudyMixin
from ..models import Study


def get_related_studies(study):
    # if no filters exist, all active studies would be related
    if not SubjectFilter.objects.filter(group__study=study).exists():
        return Study.objects.none()

    dt = timezone.now() - relativedelta(years=2)
    related_prs = Participation.objects.filter(
        updated_at__gte=dt,
        status=Participation.INVITED,
        subject__in=Subject.objects.filter(filter_queries.study(study))
    )
    return Study.objects\
        .filter(participation__in=related_prs)\
        .annotate(count=models.Count('pk'))\
        .exclude(pk=study.pk)\
        .order_by('-count')[:5]


class StudyRecruitmentSettingsUpdateView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    fields = [
        'advanced_filtering',
        'recruitment_text',
        'is_exclusive',
        'complete_matches_only',
    ]
    permission_required = 'studies.change_study'
    template_name = 'studies/study_recruitmentsettings_form.html'
    tab = 'recruitmentsettings'
    subtab = 'update'

    def get_form_class(self):
        if 'castellum.geofilters' in settings.INSTALLED_APPS:
            self.fields = [*self.fields, 'geo_filter']
        return super().get_form_class()

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExcludedStudiesView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_excluded_studies.html'
    form_class = ExcludedStudiesForm
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'excluded-studies'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = (
            Subject.objects.filter(
                filter_queries.study(self.object),
                filter_queries.has_consent()
            ).count()
        )
        context['total_count'] = Subject.objects.count()
        context['related_studies'] = list(get_related_studies(self.object))
        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyExclusionCriteriaView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_exclusioncriteria.html'
    fields = ['exclusion_criteria']
    permission_required = 'studies.change_study'
    is_onetime_invitation = False
    tab = 'recruitmentsettings'
    subtab = 'exclusioncriteria'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyRecruitmentTestMailView(StudyMixin, PermissionRequiredMixin, View):
    model = Study
    pk_url_kwarg = 'study_pk'
    permission_required = 'studies.change_study'

    def post(self, request, **kwargs):
        with MailContext('recruitment') as ctx:
            name = request.user.get_full_name()
            success = ctx.send_mail(
                self.study.mail_subject,
                self.study.mail_body.replace('{name}', name),
                [request.user.email],
                reply_to=[self.study.email],
            )

        if success:
            messages.success(self.request, _('Test mail has been sent.'))
        else:
            messages.error(self.request, _('Could not send test mail.'))

        return redirect('studies:mailsettings', self.study.pk)


class StudyMailSettingsView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_mailsettings.html'
    fields = [
        'mail_subject',
        'mail_body',
    ]
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'mailsettings'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class OneTimeInvitationMailRecruitmentView(BaseMailRecruitmentView):
    permission_required = 'studies.change_study'
    is_onetime_invitation = True
    participation_status = Participation.INVITED
    tab = 'mail'

    def form_valid(self, form):
        self._form_valid(form)
        return redirect('studies:mail', self.study.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'studies/study_base.html'
        return context
