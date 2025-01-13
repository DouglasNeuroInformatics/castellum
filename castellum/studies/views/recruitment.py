# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Participation
from castellum.recruitment.models import SubjectFilter
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext

from ..forms import MailSettingsForm
from ..forms import OtherStudiesForm
from ..forms import StudyRecruitmentSettingsForm
from ..mixins import StudyMixin
from ..models import Study


def get_related_studies(study):
    # if no filters exist, all active studies would be related
    if not SubjectFilter.objects.filter(group__study=study).exists():
        return Study.objects.none()

    dt = timezone.now() - relativedelta(years=2)
    related_prs = Participation.objects.filter(
        updated_at__gte=dt,
        status__in=Participation.INVITED_SET,
        subject__in=Subject.objects.filter(filter_queries.study_recruitable(study)),
    )
    return (
        Study.objects
        .annotate(count=models.Count('pk'))
        .filter(participation__in=related_prs)
        .exclude(pk=study.pk)
        .order_by('-count')[:5]
    )


class StudyRecruitmentSettingsUpdateView(
    StudyMixin, PermissionRequiredMixin, UpdateView
):
    model = Study
    pk_url_kwarg = 'study_pk'
    form_class = StudyRecruitmentSettingsForm
    permission_required = 'studies.change_study'
    is_filter_trial = None
    template_name = 'studies/study_recruitmentsettings_form.html'
    tab = 'recruitmentsettings'
    subtab = 'update'

    @property
    def base_template(self):
        if self.study.is_filter_trial:
            return 'studies/study_filtertrial_base.html'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class StudyOtherStudiesView(StudyMixin, PermissionRequiredMixin, UpdateView):
    model = Study
    pk_url_kwarg = 'study_pk'
    template_name = 'studies/study_other_studies.html'
    form_class = OtherStudiesForm
    permission_required = 'studies.change_study'
    is_filter_trial = None
    tab = 'recruitmentsettings'
    subtab = 'other-studies'

    @property
    def base_template(self):
        if self.study.is_filter_trial:
            return 'studies/study_filtertrial_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = (
            Subject.objects.filter(
                filter_queries.study_recruitable(self.object),
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


class StudyRecruitmentTestMailView(StudyMixin, PermissionRequiredMixin, View):
    model = Study
    pk_url_kwarg = 'study_pk'
    permission_required = 'studies.change_study'

    def post(self, request, **kwargs):
        with MailContext('recruitment') as ctx:
            name = request.user.get_full_name()
            success = ctx.send_mail(
                request.POST.get('mail_subject', ''),
                request.POST.get('mail_body', '').replace('{name}', name),
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
    form_class = MailSettingsForm
    permission_required = 'studies.change_study'
    tab = 'recruitmentsettings'
    subtab = 'mailsettings'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class FilterTrialConvertView(StudyMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'studies/study_filtertrial_convert.html'
    permission_required = 'studies.change_study'
    is_filter_trial = True
    tab = 'recruitmentsettings'
    subtab = 'convert'
