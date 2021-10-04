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

import logging
import zipfile
from urllib.parse import urlencode

from django import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from django.views.generic import View

from castellum.appointments.mixins import BaseAppointmentsUpdateView
from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.mixins import BaseContactUpdateView
from castellum.pseudonyms.forms import DomainForm
from castellum.pseudonyms.forms import PseudonymForm
from castellum.pseudonyms.helpers import get_pseudonym
from castellum.pseudonyms.helpers import get_subject
from castellum.pseudonyms.models import Domain
from castellum.recruitment.attribute_exporters import get_exporter
from castellum.recruitment.mixins import BaseAttributesUpdateView
from castellum.recruitment.mixins import ParticipationMixin
from castellum.recruitment.models import ExecutionTag
from castellum.recruitment.models import NewsMailBatch
from castellum.recruitment.models import Participation
from castellum.recruitment.models import ReliabilityEntry
from castellum.recruitment.templatetags.recruitment import study_legal_representative_hash
from castellum.studies.mixins import StudyMixin
from castellum.studies.models import Study
from castellum.subjects.mixins import BaseAdditionalInfoUpdateView
from castellum.subjects.mixins import BaseDataProtectionUpdateView
from castellum.subjects.mixins import SubjectMixin
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
            .with_appointment_count()\
            .filter(status=Participation.INVITED)\
            .prefetch_related(
                models.Prefetch('subject', queryset=Subject.objects.annotate_reliability())
            )
        for participation in participations:
            has_access = self.request.user.has_privacy_level(participation.subject.privacy_level)
            context['list'].append((participation, has_access))

        context['session_count'] = self.study.studysession_set.count()

        return context


class ExportView(StudyMixin, PermissionRequiredMixin, DetailView):
    template_name = 'execution/study_export.html'
    model = Study
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    tab = 'list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DomainForm(context=self.study)
        return context

    def export(self, domain):
        monitoring_logger.info('Attribute export: study {} by {}'.format(
            self.study.pk, self.request.user.pk
        ))

        exporter = get_exporter()
        descriptions = self.study.exportable_attributes.all()
        response = HttpResponse(content_type='application/zip')
        zresponse = zipfile.ZipFile(response, 'w')

        subjects = []
        for participation in (
            self.study.participation_set
            .filter(status=Participation.INVITED)
            .select_related('subject')
        ):
            pseudonym = get_pseudonym(participation.subject, domain.key)
            subjects.append((pseudonym, participation.subject))

        filename = exporter.get_schema_filename()
        content = exporter.get_schema(descriptions)
        with zresponse.open(filename, 'w') as fh:
            fh.write(content.encode('UTF-8'))

        filename = exporter.get_data_filename()
        content = exporter.get_data(descriptions, subjects)
        with zresponse.open(filename, 'w') as fh:
            fh.write(content.encode('UTF-8'))

        return response

    def get(self, request, **kwargs):
        if not request.user.has_privacy_level(max(
            self.study.get_invited_max_privacy_level(),
            self.study.get_exportable_attributes_max_privacy_level(),
        )):
            raise PermissionDenied
        if 'domain' in self.request.GET:
            domain = get_object_or_404(self.study.domains.all(), key=self.request.GET['domain'])
            return self.export(domain)
        elif self.study.domains.count() == 1:
            domain = self.study.domains.get()
            return self.export(domain)
        else:
            return super().get(request, **kwargs)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domains'] = [
            *self.study.domains.all(),
            *self.study.general_domains.filter(user=self.request.user),
        ]
        return context


class ParticipationPseudonymsView(ParticipationDetailMixin, DetailView):
    participation_status = [Participation.INVITED]
    study_status = []
    template_name = 'execution/participation_pseudonyms.html'
    tab = 'overview'

    def has_permission(self):
        return (
            super().has_permission()
            or self.request.user.has_perm('subjects.export_subject')
            or self.request.user.has_perm('subjects.delete_subject')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # make sure name is not used in template
        context['subject'] = None
        context['participation'] = None

        context['domains'] = self.study.domains.all()

        return context


class ParticipationPseudonymView(ParticipationDetailMixin, View):
    def has_permission(self):
        return (
            super().has_permission()
            or self.request.user.has_perm('subjects.export_subject')
            or self.request.user.has_perm('subjects.delete_subject')
        )

    def get(self, request, *args, **kwargs):
        qs = Domain.objects.filter(
            models.Q(pk__in=self.study.domains.all())
            | models.Q(pk__in=self.study.general_domains.filter(user=request.user))
        )
        domain = get_object_or_404(qs, key=kwargs['domain'])
        pseudonym = get_pseudonym(self.subject, domain.key)

        monitoring_logger.info('Pseudonym access: domain {} by {}'.format(
            domain.key, self.request.user.pk
        ))

        return HttpResponse(pseudonym)


class ParticipationDropoutView(ParticipationDetailMixin, DetailView):
    template_name = 'execution/participation_dropout.html'
    tab = 'overview'

    def post(self, request, *args, **kwargs):
        participation = self.get_object()
        participation.dropped_out = request.POST.get('dropped_out') == '1'
        participation.save()
        return redirect('execution:study-detail', participation.study.pk)


class ParticipationDropoutConfirmView(ParticipationDetailMixin, DetailView):
    template_name = 'execution/participation_dropout_confirm.html'
    tab = 'overview'

    def post(self, request, *args, **kwargs):
        participation = self.get_object()
        participation.dropped_out = True
        participation.status = Participation.UNSUITABLE
        participation.save()
        return redirect('execution:study-detail', participation.study.pk)


class ParticipationUpdateView(ParticipationDetailMixin, UpdateView):
    template_name = 'execution/participation_hints.html'
    fields = ['news_interest', 'execution_tags', 'assigned_conductor']
    tab = 'update'

    @cached_property
    def reliabilityentry(self):
        entry, __ = ReliabilityEntry.objects.get_or_create(
            study=self.object.study,
            subject=self.object.subject,
        )
        return entry

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['execution_tags'].queryset = ExecutionTag.objects.filter(study=self.study)
        form.fields['assigned_conductor'].queryset = self.study.studymembership_set.filter(
            user_id__in=[u.pk for u in self.study.conductors]
        )
        form.fields['was_reliable'] = forms.TypedChoiceField(
            label=_('Reliability'),
            initial=self.reliabilityentry.was_reliable,
            widget=forms.RadioSelect,
            coerce=lambda v: v == 'True',
            choices=[
                (True, _('I would invite this subject again for further studies')),
                (False, _(
                    'There were issues with this subject (e.g. they did not show up for '
                    'appointments without prior notice)'
                )),
            ],
        )
        return form

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        self.reliabilityentry.was_reliable = form.cleaned_data['was_reliable']
        self.reliabilityentry.save()

        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form)


class ParticipationAppointmentsUpdateView(BaseAppointmentsUpdateView):
    permission_required = ['recruitment.conduct_study', 'appointments.change_appointment']
    study_status = [Study.EXECUTION]
    participation_status = [Participation.INVITED]
    base_template = 'execution/participation_base.html'
    tab = 'appointments'


class ResolveView(StudyMixin, PermissionRequiredMixin, FormView):
    template_name = 'execution/study_resolve.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    form_class = PseudonymForm
    tab = 'pseudonym'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['context'] = self.study
        return kwargs

    def form_valid(self, form):
        try:
            subject = get_subject(form.cleaned_data['domain'], form.cleaned_data['pseudonym'])
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
        return ctx.send_separate_mails(
            subject,
            body.replace('{name}', contact.full_name),
            contact.own_or_legal_representative_emails,
            reply_to=[self.study.email],
            recipients_string=contact.email_recipients_string,
        )

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

        body = 'You sent news emails to {} subjects.'.format(len(succeeded))

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
                '[{}] news email sent'.format(self.study.name),
                body,
                [user.email for user in self.study.conductors],
            )

    def send_test_mail(self, form):
        user = self.request.user

        with MailContext('recruitment') as ctx:
            success = ctx.send_mail(
                form.cleaned_data['subject'],
                form.cleaned_data['body'].replace('{name}', user.get_full_name()),
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
            'Mail was sent to {} subjects. '
            'An email was sent to all study conductors with further information. '
            'That email also lists potential next steps.'
        ).format(len(succeeded)))

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
    base_template = 'execution/participation_update_base.html'
    tab = 'update-data'

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)

    def get_permission_required(self):
        permission_required = {'recruitment.conduct_study'}
        permission_required.update(super().get_permission_required())
        return permission_required


class ContactUpdateView(ExecutionUpdateMixin, BaseContactUpdateView):
    subtab = 'contact'
    context = 'execution'

    def get_object(self):
        return self.participation.subject.contact


class AttributesUpdateView(ExecutionUpdateMixin, BaseAttributesUpdateView):
    subtab = 'attributes'

    def get_object(self):
        return self.participation.subject


class DataProtectionUpdateView(ExecutionUpdateMixin, BaseDataProtectionUpdateView):
    subtab = 'data-protection'

    def get_object(self):
        return self.participation.subject


class AdditionalInfoUpdateView(ExecutionUpdateMixin, BaseAdditionalInfoUpdateView):
    subtab = 'additional-info'

    def get_object(self):
        return self.participation.subject


class CalendarView(StudyMixin, PermissionRequiredMixin, DetailView):
    model = Study
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    template_name = 'execution/calendar.html'
    tab = 'calendar'

    def get(self, request, *args, **kwargs):
        if 'events' in request.GET:
            url = reverse('execution:calendar-feed', args=[self.study.pk])
            return redirect(url + '?format=json&' + urlencode(request.GET))
        else:
            return super().get(request, *args, **kwargs)


class ProgressView(StudyMixin, PermissionRequiredMixin, ListView):
    model = Study
    template_name = 'execution/study_progress.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    tab = 'progress'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['invited'] = (
            self.study.participation_set
            .filter(status=Participation.INVITED)
            .count()
        )
        context['total'] = max(self.study.min_subject_count, context['invited'])
        context['sessions'] = self.study.studysession_set.annotate(
            scheduled=models.Count(
                'appointment',
                filter=models.Q(
                    appointment__participation__status=Participation.INVITED,
                ),
                distinct=True,
            ),
            took_place=models.Count(
                'appointment',
                filter=models.Q(
                    appointment__participation__status=Participation.INVITED,
                    appointment__start__lte=timezone.now(),
                ),
                distinct=True,
            ),
        ).order_by('pk')

        return context


class TagView(StudyMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'execution/study_execution_tags.html'
    permission_required = 'recruitment.conduct_study'
    study_status = [Study.EXECUTION]
    tab = 'tags'

    def get_form(self, tag=None, **kwargs):
        form_cls = forms.modelform_factory(ExecutionTag, fields=['name', 'color'])
        if tag:
            kwargs['prefix'] = tag.pk
        return form_cls(instance=tag, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['forms'] = [self.get_form(tag) for tag in self.study.executiontag_set.all()]
        context['create_form'] = self.get_form()

        return context

    def form_invalid(self):
        messages.error(self.request, _('There have been errors.'))
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if action in ['save', 'delete'] and 'id' not in request.POST:
            return self.form_invalid()
        if action not in ['create', 'save', 'delete']:
            return self.form_invalid()

        if 'id' in request.POST:
            tag = get_object_or_404(ExecutionTag, pk=request.POST['id'], study=self.study)
        else:
            tag = None

        if action in ['create', 'save']:
            form = self.get_form(tag, data=request.POST)
            if form.is_valid():
                form.instance.study = self.study
                form.save()
                messages.success(request, _('Data has been saved.'))
                return redirect('execution:execution-tags', self.study.pk)
            else:
                return self.form_invalid()
        else:
            tag.delete()
            messages.success(request, _('Tag has been deleted.'))
            return redirect('execution:execution-tags', self.study.pk)


class LegalRepresentativeContactUpdateView(StudyMixin, SubjectMixin, BaseContactUpdateView):
    base_template = 'execution/base.html'
    study_status = [Study.EXECUTION]

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form, *args):
        messages.success(self.request, _('Data has been saved.'))
        return super().form_valid(form, *args)

    def get_permission_required(self):
        permission_required = {'recruitment.conduct_study'}
        permission_required.update(super().get_permission_required())
        return permission_required

    def get_object(self):
        participation = get_object_or_404(
            Participation,
            pk=self.kwargs['participation_pk'],
            study=self.study,
            status=Participation.INVITED,
        )
        if not self.request.user.has_privacy_level(participation.subject.privacy_level):
            return self.handle_no_permission()

        for legal_representative in participation.subject.contact.legal_representatives.all():
            h = study_legal_representative_hash(self.study, legal_representative.subject)
            if h == self.kwargs['hash']:
                return legal_representative

        raise Http404
