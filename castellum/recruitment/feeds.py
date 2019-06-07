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
import abc

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.text import slugify

from django_ical.views import ICalFeed

from castellum.studies.models import Study

from .models import ParticipationRequest


class BaseAppointmentFeed(abc.ABC, ICalFeed):
    @abc.abstractmethod
    def get_object(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def items(self, study):
        pass

    @abc.abstractmethod
    def file_name(self, study):
        pass

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


class AppointmentFeedForStudy(BaseAppointmentFeed):
    def get_object(self, *args, **kwargs):
        study = Study.get_by_pk_or_404(kwargs.get('study_pk'))
        study.raise_404_error_if_study_is_not_in_recruitment_mode()
        return study

    def items(self, study):
        return ParticipationRequest.objects\
            .filter(study=study, appointment__isnull=False)\
            .order_by('-appointment')

    def file_name(self, study):
        return 'castellum-{}.ics'.format(slugify(study.name))


class AppointmentFeedForUser(BaseAppointmentFeed):
    def get_object(self, *args, **kwargs):
        return get_object_or_404(get_user_model(), pk=kwargs.get('user_id'))

    def items(self, user):
        for study in Study.objects.filter(recruitment_mode=True):
            if not (user.has_perm('recruitment.add_participationrequest', obj=study) and
                    user.has_perm('studies.access_study', obj=study)):
                continue
            qs = (ParticipationRequest.objects.filter(study=study, appointment__isnull=False)
                                              .order_by('-appointment'))
            for participation_request in qs:
                yield participation_request

    def file_name(self, study):
        return 'castellum-appointments.ics'
