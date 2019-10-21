# (c) 2018
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

import datetime
import random
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import SearchForm
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.contacts.models import Contact
from castellum.recruitment.mixins import BaseAttributeSetUpdateView
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseSubjectUpdateView
from castellum.subjects.mixins import SubjectMixin
from castellum.utils.chart import ChartRenderer
from castellum.utils.views import GetFormView

from .forms import ContactForm
from .forms import SendMailForm
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest


class StudyListView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/study_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        perms = ('recruitment.add_participationrequest', 'studies.access_study')
        return [study for study in qs.filter(study_mode=Study.EXECUTION) if (
            self.request.user.has_perms(perms, obj=study)
        )]


class RecruitmentView(StudyMixin, PermissionRequiredMixin, ListView):
    model = ParticipationRequest
    context_object_name = 'participation_requests'
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.view_participationrequest'
    study_modes = [Study.EXECUTION]
    shown_status = []
    tab = 'recruitment'

    def dispatch(self, request, *args, **kwargs):
        self.sort = self.request.GET.get('sort', self.request.session.get('recruitment_sort'))
        self.request.session['recruitment_sort'] = self.sort
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.sort == 'appointment':
            order_by = ['appointment', '-updated_at']
        elif self.sort == 'last_contact_attempt':
            order_by = ['-status_not_reached', '-updated_at']
        elif self.sort == 'created':
            order_by = ['-created_at']
        else:
            order_by = ['-appointment_today', 'status', 'appointment', '-updated_at']

        return ParticipationRequest.objects\
            .prefetch_related('subject__attributeset')\
            .filter(status__in=self.shown_status, study=self.study)\
            .order_by(*order_by)

    def get_statistics(self):
        participation_requests = ParticipationRequest.objects.filter(
            study=self.study, status=ParticipationRequest.INVITED
        ).prefetch_related('subject__attributeset')

        buckets1 = AttributeDescription.get_statistics_buckets('primary')
        buckets2 = AttributeDescription.get_statistics_buckets('secondary')

        if len(buckets1) == 1:
            return None

        statistics = defaultdict(lambda: defaultdict(lambda: 0))
        for participation_request in participation_requests:
            try:
                attributeset = participation_request.subject.attributeset
                key1 = attributeset.get_statistics_bucket('primary')
                key2 = attributeset.get_statistics_bucket('secondary')
                statistics[key1][key2] += 1
            except AttributeSet.DoesNotExist:
                pass

        data = {
            'rows': [{
                'label': str(label1),
                'values': [statistics[key1][key2] for key2, label2 in buckets2]
            } for key1, label1 in buckets1],
        }

        if len(buckets2) > 1:
            data['legend'] = [str(label2) for key2, label2 in buckets2]

        renderer = ChartRenderer(width=760, height=320)
        return renderer.render(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        buckets1 = dict(AttributeDescription.get_statistics_buckets('primary'))
        buckets2 = dict(AttributeDescription.get_statistics_buckets('secondary'))

        participants = []
        for participation_request in self.get_queryset():
            try:
                attributeset = participation_request.subject.attributeset
                bucket1 = buckets1[attributeset.get_statistics_bucket('primary')]
                bucket2 = buckets2[attributeset.get_statistics_bucket('secondary')]
                buckets = ', '.join(str(bucket) for bucket in [bucket1, bucket2] if bucket)
            except AttributeSet.DoesNotExist:
                buckets = ''

            can_access = self.request.user.has_privacy_level(
                participation_request.subject.privacy_level
            )

            participants.append((participation_request, buckets, can_access))
        context['participants'] = participants

        context['sort_options'] = [
            ('relevance', _('Relevance')),
            ('appointment', _('Follow-up date')),
            ('last_contact_attempt', _('Last contact attempt')),
            ('created', _('Added to list')),
        ]
        sort_options = dict(context['sort_options'])
        context['sort_label'] = sort_options.get(self.sort, _('Relevance'))

        context['statistics'] = self.get_statistics()

        queryset = ParticipationRequest.objects.filter(study=self.study)
        context['all_count'] = queryset.count()
        context['invited_count'] = queryset.filter(
            status=ParticipationRequest.INVITED).count()
        context['unsuitable_count'] = queryset.filter(
            status=ParticipationRequest.UNSUITABLE).count()
        context['open_count'] = queryset.filter(status__in=[
            ParticipationRequest.NOT_CONTACTED,
            ParticipationRequest.NOT_REACHED,
            ParticipationRequest.FOLLOWUP_APPOINTED,
            ParticipationRequest.AWAITING_RESPONSE,
        ]).count()

        context['last_agreeable_contact_time'] = datetime.date.today() - datetime.timedelta(
            days=settings.CASTELLUM_DAYS_BETWEEN_CONTACT_ATTEMPTS
        )

        return context


class RecruitmentViewInvited(RecruitmentView):

    shown_status = [ParticipationRequest.INVITED]
    subtab = 'invited'


class RecruitmentViewUnsuitable(RecruitmentView):
    shown_status = [ParticipationRequest.UNSUITABLE]
    subtab = 'unsuitable'


class RecruitmentViewOpen(RecruitmentView):

    shown_status = [
        ParticipationRequest.NOT_CONTACTED,
        ParticipationRequest.NOT_REACHED,
        ParticipationRequest.FOLLOWUP_APPOINTED,
        ParticipationRequest.AWAITING_RESPONSE,
    ]
    subtab = 'open'

    def create_participation_requests(self, batch_size):
        attributesets = list(AttributeSet.get_recruitable(self.study))

        added = min(batch_size, len(attributesets))
        for attributeset in random.sample(attributesets, k=added):
            ParticipationRequest.objects.create(study=self.study, subject=attributeset.subject)

        return added

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('recruitment.add_participationrequest', obj=self.study):
            raise PermissionDenied

        if self.study.min_subject_count == 0:
            messages.error(request, _(
                'This study does not require participants. '
                'Please, contact the responsible person who can set it up.'
            ))
            return self.get(request, *args, **kwargs)

        not_contacted_count = self.get_queryset()\
            .filter(status=ParticipationRequest.NOT_CONTACTED).count()
        hard_limit = self.study.min_subject_count * settings.CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR

        if not_contacted_count >= hard_limit:
            messages.error(request, _(
                'Application privacy does not allow you to add more subjects. '
                'Please contact provided subjects before adding new ones.'
            ))
            return self.get(request, *args, **kwargs)

        # Silently trim down to respect hard limit.
        # In many cases, the soft limit warning will already be shown in that case.
        batch_size = min(
            settings.CASTELLUM_RECRUITMENT_BATCH_SIZE,
            hard_limit - not_contacted_count,
        )
        try:
            added = self.create_participation_requests(batch_size)
        except KeyError:
            added = 0
            messages.error(request, _(
                'The custom filter that is set for this study does not exist.'
            ))

        if not_contacted_count + added > settings.CASTELLUM_RECRUITMENT_SOFT_LIMIT:
            messages.error(request, _(
                'Such workflow is not intended due to privacy reasons. '
                'Please contact provided subjects before adding new ones.'
            ))

        if added < batch_size:
            messages.error(request, _('We cannot find participants for this study.'))

        return self.get(request, *args, **kwargs)


class MailRecruitmentView(StudyMixin, PermissionRequiredMixin, FormView):
    permission_required = 'recruitment.view_participationrequest'
    template_name = 'recruitment/mail.html'
    tab = 'mail'
    form_class = SendMailForm

    def create_participation_requests(self, batch_size):
        attributesets = list(AttributeSet.get_recruitable(self.study))

        connection = get_connection()
        counter = 0
        while counter < batch_size and attributesets:
            pick = attributesets.pop(random.randrange(0, len(attributesets)))
            if pick.subject.contact.email:
                mail = EmailMessage(
                    self.study.mail_subject,
                    self.study.mail_body,
                    self.study.mail_reply_address,
                    [pick.subject.contact.email],
                    connection=connection,
                )
                success = mail.send()
                if success:
                    ParticipationRequest.objects.create(study=self.study, subject=pick.subject)
                    counter += 1

        confirmation = EmailMessage(
            self.study.mail_subject,
            '%i emails have been sent.\n\n---\n\n%s' % (counter, self.study.mail_body),
            self.study.mail_reply_address,
            [self.study.mail_reply_address],
            connection=connection,
        )
        confirmation.send()

        return counter

    def form_valid(self, form):
        batch_size = form.cleaned_data['batch_size']
        try:
            added = self.create_participation_requests(batch_size)
        except KeyError:
            added = 0
            messages.error(self.request, _(
                'The custom filter that is set for this study does not exist.'
            ))

        if added > 0:
            messages.success(self.request, _('Mails have been sent.'))

        if added < batch_size:
            messages.error(self.request, _('We cannot find participants for this study.'))

        return redirect('recruitment:mail', self.study.pk)


class ContactView(StudyMixin, SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = ParticipationRequest
    form_class = ContactForm
    template_name = 'recruitment/contact.html'
    permission_required = (
        'contacts.view_contact',
        'recruitment.change_participationrequest',
    )
    study_modes = [Study.EXECUTION]

    def get_initial(self):
        initial = super().get_initial()
        if self.object.match:
            initial['status'] = None
        else:
            initial['status'] = ParticipationRequest.UNSUITABLE
        initial['appointment'] = None
        return initial

    def get_object(self):
        return get_object_or_404(ParticipationRequest, study=self.study, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(ParticipationRequest.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        context['context'] = self.request.GET.get('context')
        context['contact'] = self.object.subject.contact

        return context

    def get_success_url(self):
        context = self.request.GET.get('context')
        if context == 'subjects:studyparticipation':
            return reverse(context, args=[self.object.subject.pk])
        else:
            return reverse('recruitment:recruitment-open', args=[self.object.study.pk])


class ContactUpdateView(StudyMixin, BaseContactUpdateView):
    study_modes = [Study.EXECUTION]

    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pk=self.kwargs['pk'])

        return participation_request.subject.contact

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['pk']])

    def get_cancel_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "recruitment/base.html"
        return context


class AttributeSetUpdateView(StudyMixin, BaseAttributeSetUpdateView):
    study_modes = [Study.EXECUTION]

    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pk=self.kwargs['pk'])
        return participation_request.subject.attributeset

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['pk']])

    def get_cancel_url(self):
        return self.get_success_url()


class SubjectUpdateView(StudyMixin, BaseSubjectUpdateView):
    study_modes = [Study.EXECUTION]

    def get_object(self):
        participation_request = get_object_or_404(
            ParticipationRequest, study=self.study, pk=self.kwargs['pk'])
        return participation_request.subject

    def get_success_url(self):
        return reverse('recruitment:contact', args=[self.kwargs['study_pk'], self.kwargs['pk']])

    def get_cancel_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "recruitment/base.html"
        return context


class SearchView(LoginRequiredMixin, GetFormView):
    template_name = 'recruitment/search.html'
    form_class = SearchForm

    def get_matches(self, form):
        contacts = Contact.objects.fuzzy_filter(**form.cleaned_data)
        subjects = [c.subject for c in contacts]
        participation_requests = ParticipationRequest.objects.filter(
            subject__in=subjects, study__study_mode=Study.EXECUTION
        ).select_related('subject', 'study')

        result = {}
        perms = ('studies.access_study',) + ContactView.permission_required
        for pr in participation_requests:
            if (
                self.request.user.has_perms(perms, pr.study) and
                self.request.user.has_privacy_level(pr.subject.privacy_level)
            ):
                result.setdefault(pr.subject, [])
                result[pr.subject].append(pr)

        return list(result.items())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form')
        if form and form.is_valid():
            context['object_list'] = self.get_matches(form)
        return context
