# (c) 2018-2020
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
import logging
import zipfile

from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import UpdateView

from castellum.appointments.forms import AppointmentsForm
from castellum.appointments.mixins import BaseCalendarView
from castellum.appointments.mixins import send_appointment_notifications
from castellum.appointments.models import Appointment
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_subject
from castellum.recruitment.attribute_exporters import get_exporter
from castellum.recruitment.mixins import BaseAttributesUpdateView
from castellum.recruitment.mixins import ParticipationMixin
from castellum.recruitment.models import NewsMailBatch
from castellum.recruitment.models import Participation
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.subjects.models import Subject
from castellum.utils.mail import MailContext

from .forms import NewsMailForm

monitoring_logger = logging.getLogger('monitoring.execution')


class StudyDetailView(StudyMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/study_detail.html'
    model = Study
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    tab = 'list'

    def get_object(self):
        return self.study

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['list'] = []
        participations = self.study.participation_set\
            .annotate(appointment_count=models.Count('appointment'))\
            .filter(status=Participation.INVITED)\
            .prefetch_related(
                models.Prefetch('subject', queryset=Subject.objects.annotate_showup())
            )
        for participation in participations:
            has_access = self.request.user.has_privacy_level(participation.subject.privacy_level)
            context['list'].append((participation, has_access))

        context['session_count'] = self.study.studysession_set.count()

        return context

    def export(self):
        monitoring_logger.info('Attribute export: study {} by {}'.format(
            self.study.pk, self.request.user.pk
        ))

        exporter = get_exporter()
        descriptions = self.study.exportable_attributes.all()
        response = HttpResponse(content_type='application/zip')
        zresponse = zipfile.ZipFile(response, 'w')

        subjects = []
        for participation in self.study.participation_set.filter(status=Participation.INVITED):
            has_access = self.request.user.has_privacy_level(participation.subject.privacy_level)
            if has_access:
                subjects.append((participation.pseudonym, participation.subject))

        filename = exporter.get_schema_filename()
        content = exporter.get_schema(descriptions)
        with zresponse.open(filename, 'w') as fh:
            fh.write(content.encode('UTF-8'))

        filename = exporter.get_data_filename()
        content = exporter.get_data(descriptions, subjects)
        with zresponse.open(filename, 'w') as fh:
            fh.write(content.encode('UTF-8'))

        return response

    def get(self, request, *args, **kwargs):
        if 'export' in request.GET:
            return self.export()
        else:
            return super().get(request, *args, **kwargs)


class ParticipationDetailMixin(ParticipationMixin, PermissionRequiredMixin):
    model = Participation
    permission_required = ['recruitment.conduct_study']
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]

    def get_object(self, queryset=None):
        return self.participation


class ParticipationDetailView(ParticipationDetailMixin, DetailView):
    template_name = 'execution/participation_detail.html'
    tab = 'overview'


class ParticipationNewsView(ParticipationDetailMixin, UpdateView):
    template_name = 'execution/participation_news.html'
    fields = ['news_interest']
    tab = 'news'

    def get_success_url(self):
        return reverse(
            'execution:participation-news',
            args=[self.object.study.pk, self.object.pk],
        )

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class ParticipationAppointmentsView(ParticipationDetailMixin, DetailView):
    template_name = 'execution/participation_appointments.html'
    tab = 'appointments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # The forms post to ShowUpUpdateView
        context['appointments'] = []
        form_cls = forms.modelform_factory(Appointment, fields=['show_up'])
        for session, appointment in self.object.get_appointments():
            form = form_cls(instance=appointment)
            context['appointments'].append((session, appointment, form))

        return context


class ParticipationAppointmentsUpdateView(ParticipationDetailMixin, UpdateView):
    template_name = 'execution/participation_appointments_form.html'
    permission_required = ['recruitment.conduct_study', 'appointments.change_appointment']
    form_class = AppointmentsForm
    tab = 'appointments'

    def get_success_url(self):
        return reverse('execution:participation-appointments', args=[
            self.object.study.pk, self.object.pk
        ])

    def form_valid(self, form):
        response = super().form_valid(form)
        send_appointment_notifications(self.request, self.object, form.appointment_changes)
        return response


class ShowUpUpdateView(ParticipationMixin, UpdateView):
    # Used by ParticipationAppointmentsView

    model = Appointment
    fields = ['show_up']
    http_method_names = ['post']
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]

    def get_object(self):
        return get_object_or_404(
            Appointment,
            pk=self.kwargs['appointment_pk'],
            participation=self.participation,
        )

    def get_success_url(self):
        return reverse(
            'execution:participation-appointments',
            args=[self.kwargs['study_pk'], self.kwargs['pk']],
        )

    def form_valid(self, form):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class ResolveView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'execution/study_resolve.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    form_class = PseudonymForm
    tab = 'pseudonym'

    def form_valid(self, form):
        try:
            subject = get_subject(self.study.domain, form.cleaned_data['pseudonym'])
            participation = Participation.objects.filter(
                study=self.study,
                subject=subject,
                status=Participation.INVITED,
            ).get()
            return redirect('execution:participation-detail', self.study.pk, participation.pk)
        except ObjectDoesNotExist:
            messages.warning(self.request, _('No match found'))
            return self.render_to_response(self.get_context_data(form=form))


class NewsMailView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'execution/study_news_mail.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    form_class = NewsMailForm
    tab = 'news'

    def send_mail(self, ctx, participation, subject=None, body=None):
        contact = participation.subject.contact
        count = 0
        for email in contact.own_or_guardian_emails:
            count += ctx.send_mail(
                subject,
                body.replace('{name}', contact.full_name),
                [email],
                reply_to=[self.study.email],
                recipients_string=contact.email_recipients_string,
            )
        return count

    def render_urls(self, participations):
        return '\n'.join(
            self.request.build_absolute_uri(reverse(
                'execution:participation-detail',
                args=[self.study.pk, participation.pk],
            ))
            for participation in participations
        )

    def send_summary(self, succeeded, failed, form):
        postal = list(self.study.participation_set.filter(
            news_interest=Participation.VIA_POSTAL
        ))

        body = 'You sent news emails to %i subjects.' % len(succeeded)

        if failed:
            body += (
                '\n\nThe following subjects asked to be informed via '
                'email but could not be reached:\n'
            )
            body += self.render_urls(failed)

        if postal:
            body += '\n\nThe following subjects asked to be informed via postal mail:\n'
            body += self.render_urls(postal)

        body += '\n\n-------- Original Message --------\n'
        body += 'Subject: {subject}\n\n{body}'.format(**form.cleaned_data)

        NewsMailBatch.objects.create(
            study=self.study,
            contacted_size=len(succeeded),
            other_size=len(failed) + len(postal),
            mail_subject=form.cleaned_data['subject'],
            mail_body=form.cleaned_data['body'],
        )

        with MailContext('internal') as ctx:
            return ctx.send_mail(
                '[%s] news email send' % self.study.name,
                body,
                [user.email for user in self.study.conductors],
            )

    def send_test_mail(self, form):
        user = self.request.user
        name = user.get_full_name() or user.username

        with MailContext('recruitment') as ctx:
            success = ctx.send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['body'].replace('{name}', name),
                [user.email],
                reply_to=[self.study.email],
            )

        if success:
            messages.success(self.request, _('Test mail has been sent.'))
        else:
            messages.error(self.request, _('Could not send test mail.'))

        return self.form_invalid(form)

    def form_valid(self, form):
        if 'testmail' in form.data:
            return self.send_test_mail(form)

        interested = self.study.participation_set.filter(
            news_interest=Participation.VIA_EMAIL
        )

        if interested.count() == 0:
            messages.warning(self.request, _(
                'None of the subjects signed up for news emails.'
            ))
            return self.form_invalid(form)

        succeeded = []
        failed = []

        with MailContext('recruitment') as ctx:
            for participation in interested:
                success = self.send_mail(ctx, participation, **form.cleaned_data)
                if success:
                    succeeded.append(participation)
                else:
                    failed.append(participation)

        self.send_summary(succeeded, failed, form)
        messages.success(self.request, _(
            'Mail was sent to %i subjects. '
            'An email was sent to all study conductors with further information. '
            'That email also lists potential next steps.'
        ) % len(succeeded))

        return redirect('execution:news-mail', self.study.pk)


class ExclusionCriteriaView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = Study
    template_name = 'execution/participation_criteria.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    tab = 'criteria'


class ExecutionUpdateMixin(ParticipationMixin):
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]
    tab = 'overview'

    def get_success_url(self):
        return reverse(
            'execution:participation-detail',
            args=[self.kwargs['study_pk'], self.kwargs['pk']],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = "execution/participation_base.html"
        return context

    def get_permission_required(self):
        permission_required = {'recruitment.conduct_study'}
        permission_required.update(super().get_permission_required())
        return permission_required


class ContactUpdateView(ExecutionUpdateMixin, BaseContactUpdateView):
    def get_object(self):
        return self.participation.subject.contact


class AttributesUpdateView(ExecutionUpdateMixin, BaseAttributesUpdateView):
    def get_object(self):
        return self.participation.subject


class DataProtectionUpdateView(ExecutionUpdateMixin, BaseDataProtectionUpdateView):
    def get_object(self):
        return self.participation.subject


class AdditionalInfoUpdateView(ExecutionUpdateMixin, BaseAdditionalInfoUpdateView):
    def get_object(self):
        return self.participation.subject


class CalendarView(StudyMixin, PermissionRequiredMixin, BaseCalendarView):
    model = Study
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    template_name = 'execution/calendar.html'
    tab = 'calendar'

    def render_appointment(self, appointment):
        return {
            'title': appointment.session.name,
            'start': appointment.start,
            'end': appointment.end,
            'url': reverse('execution:participation-detail', args=[
                self.object.pk, appointment.participation.pk
            ]),
        }

    def get_appointments(self):
        return super().get_appointments().filter(session__study=self.object)


class ReceptionView(PermissionRequiredMixin, ListView):
    model = Appointment
    template_name = 'execution/reception.html'
    permission_required = 'appointments.view_current_appointments'

    def get_queryset(self):
        return super().get_queryset().filter(
            participation__status=Participation.INVITED,
            start__date=datetime.date.today(),
        ).order_by('start')
