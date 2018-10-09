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

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.contacts.models import Contact
from castellum.pseudonyms.helpers import resolve_pseudonym
from castellum.settings import CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
from castellum.settings import CASTELLUM_RECRUITMENT_SOFT_LIMIT
from castellum.studies.models import Study

from ..models import AttributeSet
from ..models import ParticipationRequest
from .mixins import PublishedStudyMixin

monitoring_logger = logging.getLogger('monitoring.recruitment')


class StudyChoiceView(LoginRequiredMixin, ListView):
    model = Study
    context_object_name = 'studies'
    template_name = 'recruitment/studies_list.html'


class RecruitmentView(LoginRequiredMixin, PublishedStudyMixin, ListView):
    model = ParticipationRequest
    context_object_name = 'participation_requests'
    template_name = 'recruitment/recruitment.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        participants = []
        for participation in self.get_queryset():
            contact_pseudonym = resolve_pseudonym(
                self.study.domain,
                participation.pseudonym,
                Contact.domain)
            contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)
            participants.append((participation, contact))
        context['participants'] = participants

        queryset = ParticipationRequest.objects.filter(study=self.study)
        context['all_count'] = queryset.count()
        context['invited_count'] = queryset.filter(
            status=ParticipationRequest.INVITED).count()
        context['unsuitable_count'] = queryset.filter(
            status=ParticipationRequest.UNSUITABLE).count()
        context['not_reached_count'] = queryset.filter(
            status=ParticipationRequest.NOT_REACHED).count()
        context['not_contacted_count'] = queryset.filter(
            status=ParticipationRequest.NOT_CONTACTED).count()
        context['study'] = self.study
        return context


class RecruitmentViewNotReached(RecruitmentView):

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter_not_reached(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['not_reached_view'] = True
        return context


class RecruitmentViewNotContacted(RecruitmentView):

    def pick_random(self, qs):
        count = qs.count()
        if count != 0:
            random_index = random.randint(0, count - 1)
            return qs.all()[random_index]

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects
        return queryset.filter_not_contacted(study=self.study)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['not_contacted_view'] = True
        return context

    def post(self, request, *args, **kwargs):
        if self.study.min_subjects_count is None:
            messages.error(request, _('The minimal number of subjects is not set for this study. '
                                      'Please, contact the responsible person who can set it up.'))
            return self.get(request, *args, **kwargs)

        if self.study.min_subjects_count == 0:
            messages.error(request, _('This study does not require participants. '
                                      'Please, contact the responsible person who can set it up.'))
            return self.get(request, *args, **kwargs)

        not_contacted_count = self.get_queryset().count()

        if not_contacted_count >= \
           self.study.min_subjects_count*CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR:
            messages.error(request, _(
                'Application privacy does not allow you to add more subjects. '
                'Please contact provided subjects before adding new ones.'
                ))
            return self.get(request, *args, **kwargs)

        if not_contacted_count >= CASTELLUM_RECRUITMENT_SOFT_LIMIT:
            messages.error(request, _(
                'Such workflow is not intended due to privacy reasons. '
                'Please contact provided subjects before adding new ones.'
            ))

        attributeset = self.pick_random(AttributeSet.apply_study_filter(self.study))

        if attributeset is None:
            messages.error(request, _('We cannot find participants for this study.'))
            return self.get(request, *args, **kwargs)

        participation_request_pseudonym = resolve_pseudonym(
            AttributeSet.domain,
            attributeset.pseudonym,
            self.study.domain)

        __, created = ParticipationRequest.objects.get_or_create(
            study=self.study, pseudonym=participation_request_pseudonym)
        if not created:
            messages.error(request, _(
                'Picked person already participates in the study. You can '
                'just try again. But this might indicate that there are not '
                'many matches left.'))

        return self.get(request, *args, **kwargs)


class ContactView(LoginRequiredMixin, PublishedStudyMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact.html'

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects

        if self.kwargs['path'] == 'not-contacted':
            return queryset.filter_not_contacted(study=self.study)
        elif self.kwargs['path'] == 'not-reached':
            return queryset.filter_not_reached(study=self.study)
        else:
            raise Http404

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(ParticipationRequest.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        contact_pseudonym = resolve_pseudonym(
            self.study.domain,
            self.object.pseudonym,
            Contact.domain)
        contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)

        context['path'] = self.kwargs['path']
        context['study'] = self.study
        context['contact'] = contact
        return context

    def form_valid(self, form):
        # needs to be executed before object.save()
        pseudonyms = list(self.get_queryset().values_list("pseudonym", flat=True))

        self.object = form.save()

        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

        next_pseudonym_idx = None
        if "btn_back" not in form.data and len(pseudonyms) - 1 != 0:
            current_pseudonym_idx = pseudonyms.index(self.object.pseudonym)
            if current_pseudonym_idx + 1 < len(pseudonyms):
                next_pseudonym_idx = current_pseudonym_idx + 1
            elif self.kwargs['path'] == 'not-contacted':
                next_pseudonym_idx = current_pseudonym_idx - 1

        if next_pseudonym_idx is None:
            url = 'recruitment:recruitment_' + self.kwargs['path']
            return redirect(url, self.object.study.pk)
        else:
            return redirect(
                'recruitment:contact',
                self.object.study.pk,
                pseudonyms[next_pseudonym_idx],
                self.kwargs['path'])
