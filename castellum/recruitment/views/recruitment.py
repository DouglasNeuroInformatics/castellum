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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import SubjectMixin
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

    def get_queryset(self):
        qs = super().get_queryset()
        return [study for study in qs.filter(published=True) if (
            self.request.user.has_perm('recruitment.add_participationrequest', obj=study) and
            self.request.user.has_perm('studies.access_study', obj=study)
        )]


class RecruitmentView(PublishedStudyMixin, PermissionRequiredMixin, ListView):
    model = ParticipationRequest
    context_object_name = 'participation_requests'
    template_name = 'recruitment/recruitment.html'
    permission_required = 'recruitment.view_participationrequest'
    shown_status = None

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = self.model.objects

        if self.shown_status is not None:
            return queryset.filter(status=self.shown_status, study=self.study)
        else:
            return queryset.filter(study=self.study)

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)

        participants = []
        privacy_level_user = self.request.user.get_privacy_level()
        for participation in self.get_queryset():
            contact_pseudonym = resolve_pseudonym(
                self.study.domain,
                participation.pseudonym,
                Contact.domain)
            contact = get_object_or_404(Contact, pseudonym=contact_pseudonym)
            can_access = privacy_level_user >= contact.privacy_level
            participants.append((participation, contact, can_access))
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

        if self.shown_status == self.model.NOT_REACHED:
            context['not_reached_view'] = True
        elif self.shown_status == self.model.NOT_CONTACTED:
            context['not_contacted_view'] = True
        elif self.shown_status == self.model.UNSUITABLE:
            context['unsuitable_view'] = True
        elif self.shown_status == self.model.INVITED:
            context['invited_view'] = True

        return context


class RecruitmentViewNotReached(RecruitmentView):

    shown_status = ParticipationRequest.NOT_REACHED


class RecruitmentViewInvited(RecruitmentView):

    shown_status = ParticipationRequest.INVITED


class RecruitmentViewUnsuitable(RecruitmentView):

    shown_status = ParticipationRequest.UNSUITABLE


class RecruitmentViewNotContacted(RecruitmentView):

    shown_status = ParticipationRequest.NOT_CONTACTED

    def create_participation_request(self):

        attributesets = list(AttributeSet.apply_study_filter(self.study).values_list('pseudonym',
                                                                                     flat=True))

        while len(attributesets) > 0:

            pseudonym = random.choice(attributesets)

            participation_request_pseudonym = resolve_pseudonym(
                settings.DOMAINS['attributeset'],
                pseudonym,
                self.study.domain)

            participation_request, created = ParticipationRequest.objects.get_or_create(
                study=self.study, pseudonym=participation_request_pseudonym)

            if created:
                return participation_request
            else:
                attributesets.remove(pseudonym)

        return None

    def post(self, request, *args, **kwargs):
        if not request.user.has_perm('recruitment.add_participationrequest'):
            raise PermissionDenied

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

        if self.create_participation_request() is None:
            messages.error(request, _('We cannot find participants for this study.'))

        return self.get(request, *args, **kwargs)


class ContactView(PublishedStudyMixin, SubjectMixin, PermissionRequiredMixin, UpdateView):
    model = ParticipationRequest
    fields = ['status']
    slug_field = 'pseudonym'
    template_name = 'recruitment/contact.html'
    permission_required = 'recruitment.change_participationrequest'

    def get_initial(self):
        initial = super().get_initial()
        initial['status'] = None
        return initial

    def get_queryset(self, queryset=None):
        if not queryset:
            queryset = ParticipationRequest.objects

        if self.kwargs['path'] == 'not-contacted':
            return queryset.filter(status=ParticipationRequest.NOT_CONTACTED, study=self.study)
        elif self.kwargs['path'] == 'not-reached':
            return queryset.filter(status=ParticipationRequest.NOT_REACHED, study=self.study)
        elif self.kwargs['path'] != 'contacts':
            raise Http404

        return queryset

    def get_object(self, queryset=None):
        if self.kwargs['path'] != 'contacts':
            return super().get_object(queryset=queryset)
        if not queryset:
            queryset = self.get_queryset()
        obj, __ = queryset.get_or_create(pseudonym=self.kwargs['slug'], study=self.study)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        choices = [(None, '---')] + list(ParticipationRequest.STATUS_OPTIONS[1:])
        status_field = context['form'].fields['status']
        status_field.widget.choices = choices

        context['path'] = self.kwargs['path']
        context['study'] = self.study
        context['contact'] = self.contact
        return context

    def save(self, form):
        self.object = form.save()

        monitoring_logger.info('SubjectData update: {}:{} by {}'.format(
            self.study.domain,
            self.object.pseudonym,
            self.request.user.pk))

    def form_valid_recruitment(self, form):
        # needs to be executed before object.save()
        pseudonyms = list(self.get_queryset().values_list("pseudonym", flat=True))

        self.save(form)

        next_pseudonym_idx = None
        if "btn_back" not in form.data and len(pseudonyms) - 1 != 0:
            current_pseudonym_idx = pseudonyms.index(self.object.pseudonym)
            user_privacy_level = self.request.user.get_privacy_level()

            idx = current_pseudonym_idx + 1
            while idx < len(pseudonyms):
                contact = Contact.objects.get(pseudonym=resolve_pseudonym(
                    self.study.domain, pseudonyms[idx], Contact.domain))
                if contact.privacy_level <= user_privacy_level:
                    next_pseudonym_idx = idx
                    break
                idx += 1

            if next_pseudonym_idx is None and self.kwargs['path'] == 'not-contacted':
                idx = current_pseudonym_idx - 1
                while idx >= 0:
                    contact = Contact.objects.get(pseudonym=resolve_pseudonym(
                        self.study.domain, pseudonyms[idx], Contact.domain))
                    if contact.privacy_level <= user_privacy_level:
                        next_pseudonym_idx = idx
                        break
                    idx -= 1

        if next_pseudonym_idx is None:
            url = 'recruitment:recruitment_' + self.kwargs['path']
            return redirect(url, self.object.study.pk)
        else:
            return redirect(
                'recruitment:contact',
                self.object.study.pk,
                pseudonyms[next_pseudonym_idx],
                self.kwargs['path'])

    def form_valid(self, form):
        if self.kwargs['path'] == 'contacts':
            self.save(form)
            contact_pseudonym = resolve_pseudonym(
                self.study.domain,
                self.object.pseudonym,
                Contact.domain)
            return redirect('contacts:detail', contact_pseudonym)
        else:
            return self.form_valid_recruitment(form)
