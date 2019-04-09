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

import logging
import random
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import UpdateView

from django_ical.views import ICalFeed

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import SubjectMixin
from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.settings import CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
from castellum.settings import CASTELLUM_RECRUITMENT_SOFT_LIMIT
from castellum.studies.models import Study
from castellum.utils.chart import ChartRenderer

from .mixins import StudyPermissionMixin
from ..models import AttributeDescription
from ..models import AttributeSet
from ..models import ParticipationRequest

monitoring_logger = logging.getLogger('monitoring.recruitment')


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return [study for study in qs.filter(published=True) if (
            self.request.user.has_perm('recruitment.add_participationrequest', obj=study) and
            self.request.user.has_perm('studies.access_study', obj=study)
        )]


class RecruitmentView(StudyPermissionMixin, PermissionRequiredMixin, ListView):
    model = ParticipationRequest
    context_object_name = 'participation_requests'
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.view_participationrequest'
    shown_status = []
    tab = None

    def dispatch(self, request, *args, **kwargs):
        self.study = Study.get_by_pk_or_404(self.kwargs.get('study_pk'))
        self.study.raise_404_error_if_study_is_not_published()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = self.model.objects

        sort = self.request.GET.get('sort')
        if sort == 'appointment':
            order_by = ['appointment', '-updated_at']
        elif sort == 'last_call_attempt':
            order_by = ['-status_not_reached', '-updated_at']
        elif sort == 'created':
            order_by = ['-created_at']
        else:
            order_by = ['-appointment_today', 'status', 'appointment', '-updated_at']

        return queryset\
            .filter(status__in=self.shown_status, study=self.study)\
            .order_by(*order_by)

    def get_statistics(self):
        participation_requests = ParticipationRequest.objects.filter(
            study=self.study, status=ParticipationRequest.INVITED)

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
        context = super(ListView, self).get_context_data(**kwargs)

        buckets1 = dict(AttributeDescription.get_statistics_buckets('primary'))
        buckets2 = dict(AttributeDescription.get_statistics_buckets('secondary'))

        participants = []
        for participation in self.get_queryset():
            try:
                attributeset = participation.subject.attributeset
                bucket1 = buckets1[attributeset.get_statistics_bucket('primary')]
                bucket2 = buckets2[attributeset.get_statistics_bucket('secondary')]
                buckets = ', '.join(str(bucket) for bucket in [bucket1, bucket2] if bucket)
            except AttributeSet.DoesNotExist:
                buckets = ''

            can_access = self.request.user.has_privacy_level(participation.subject.privacy_level)

            participants.append((participation, buckets, can_access))
        context['participants'] = participants

        context['sort_options'] = [
            ('relevance', _('Relevance')),
            ('appointment', _('Recall date')),
            ('last_call_attempt', _('Last call attempt')),
            ('created', _('Added to list')),
        ]
        sort_options = dict(context['sort_options'])
        context['sort_label'] = sort_options.get(self.request.GET.get('sort'), _('Relevance'))

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
            ParticipationRequest.RECALL_APPOINTED,
        ]).count()
        context['study'] = self.study

        return context


class RecruitmentViewInvited(RecruitmentView):

    shown_status = [ParticipationRequest.INVITED]
    tab = 'invited'


class RecruitmentViewUnsuitable(RecruitmentView):

    shown_status = [ParticipationRequest.UNSUITABLE]
    tab = 'unsuitable'


class RecruitmentViewOpen(RecruitmentView):

    shown_status = [
        ParticipationRequest.NOT_CONTACTED,
        ParticipationRequest.NOT_REACHED,
        ParticipationRequest.RECALL_APPOINTED,
    ]
    tab = 'open'

    def create_participation_requests(self, batch_size):
        attributesets = list(
            AttributeSet
            .apply_study_filter(self.study)
            .exclude(subject__participationrequest__study=self.study)
        )

        if len(attributesets) == 0:
            return 0

        added = min(batch_size, len(attributesets))
        for attributeset in random.sample(attributesets, k=added):
            ParticipationRequest.objects.create(study=self.study, subject=attributeset.subject)

        return added

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('recruitment.add_participationrequest', obj=self.study):
            raise PermissionDenied

        if self.study.min_subjects_count == 0:
            messages.error(request, _(
                'This study does not require participants. '
                'Please, contact the responsible person who can set it up.'
            ))
            return self.get(request, *args, **kwargs)

        open_count = self.get_queryset().count()
        hard_limit = self.study.min_subjects_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR

        if open_count >= hard_limit:
            messages.error(request, _(
                'Application privacy does not allow you to add more subjects. '
                'Please contact provided subjects before adding new ones.'
            ))
            return self.get(request, *args, **kwargs)

        # Silently trim down to respect hard limit.
        # In many cases, the soft limit warning will already be shown in that case.
        batch_size = min(settings.CASTELLUM_RECRUITMENT_BATCH_SIZE, hard_limit - open_count)
        added = self.create_participation_requests(batch_size)

        if open_count + added > CASTELLUM_RECRUITMENT_SOFT_LIMIT:
            messages.error(request, _(
                'Such workflow is not intended due to privacy reasons. '
                'Please contact provided subjects before adding new ones.'
            ))

        if added < batch_size:
            messages.error(request, _('We cannot find participants for this study.'))

        return self.get(request, *args, **kwargs)


class ContactView(StudyPermissionMixin, SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status', 'appointment']
    template_name = 'recruitment/contact.html'
    permission_required = (
        'contacts.view_contact',
        'recruitment.change_participationrequest',
    )

    def dispatch(self, request, *args, **kwargs):
        self.study = Study.get_by_pk_or_404(self.kwargs.get('study_pk'))
        self.study.raise_404_error_if_study_is_not_published()
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['status'] = None
        initial['appointment'] = None
        return initial

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects

        return queryset.filter(status__in=[
            ParticipationRequest.NOT_CONTACTED,
            ParticipationRequest.NOT_REACHED,
            ParticipationRequest.RECALL_APPOINTED,
        ], study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(ParticipationRequest.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        contact_pseudonym = get_pseudonym(self.object.subject, Contact.domain)
        contact = Contact.objects.get(pseudonym=contact_pseudonym)

        context['is_contacts'] = 'contacts' in self.request.GET
        context['study'] = self.study
        context['contact'] = contact
        return context

    def save(self, form):
        self.object = form.save()

        monitoring_logger.info('ParticipationRequest update: {} by {}'.format(
            self.object.pk, self.request.user.pk))

    def form_valid_recruitment(self, form):
        # needs to be executed before object.save()
        user_privacy_level = self.request.user.get_privacy_level()
        participation_requests = list(
            self.get_queryset().filter(subject__privacy_level__lte=user_privacy_level))

        self.save(form)

        if "btn_back" not in form.data:
            current_index = [p.pk for p in participation_requests].index(self.object.pk)
            if current_index + 1 < len(participation_requests):
                participation_request = participation_requests[current_index + 1]
                return redirect(
                    'recruitment:contact', self.object.study.pk, participation_request.pk)

        return redirect('recruitment:recruitment_open', self.object.study.pk)

    def form_valid(self, form):
        if 'contacts' in self.request.GET:
            self.save(form)
            return redirect('contacts:detail', self.object.subject.pk)
        else:
            return self.form_valid_recruitment(form)


class AppointmentFeed(ICalFeed):
    def get_object(self, *args, **kwargs):
        study = Study.get_by_pk_or_404(kwargs.get('study_pk'))
        study.raise_404_error_if_study_is_not_published()
        return study

    def file_name(self, study):
        return 'castellum-{}.ics'.format(slugify(study.name))

    def items(self, study):
        return ParticipationRequest.objects\
            .filter(study=study, appointment__isnull=False)\
            .order_by('-appointment')

    def item_title(self, item):
        return '{} - {}'.format(item.study.name, item.pk)

    def item_start_datetime(self, item):
        return item.appointment

    def item_updateddate(self, item):
        return item.updated_at

    def item_description(self, item):
        return item.pk

    def item_link(self, item):
        return reverse('recruitment:contact', args=[item.study.pk, item.pk])
