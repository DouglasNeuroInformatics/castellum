# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
from io import StringIO

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from castellum.castellum_auth.mixins import PermissionRequiredMixin
from castellum.contacts.forms import BlockListFileForm
from castellum.contacts.forms import BlockListForm
from castellum.contacts.models import BlockHash
from castellum.contacts.models import Contact
from castellum.contacts.models import PotentialDuplicateError


class BlockListMixin(PermissionRequiredMixin):
    permission_required = 'contacts.view_blockhash'

    def is_blocked(self, first_name, last_name, year_of_birth):
        if BlockHash.is_blocked(first_name, last_name, year_of_birth):
            return True
        try:
            contact = Contact.objects.fuzzy_find(first_name, last_name)
            if contact:
                contacts = [contact]
            else:
                contacts = []
        except PotentialDuplicateError as e:
            contacts = e.duplicates
        for contact in contacts:
            if contact.date_of_birth and contact.date_of_birth.year != year_of_birth:
                continue
            if contact.subject.blocked or contact.subject.to_be_deleted:
                return True
            elif contact.subject.consent and contact.subject.consent.document is None:
                # NOTE: also blocks excluded_by_us
                return True
        return False


class BlockListFormView(BlockListMixin, FormView):
    form_class = BlockListForm
    template_name = 'subjects/blocklist_form.html'

    def form_valid(self, form):
        return self.render_to_response(
            self.get_context_data(
                form=form,
                is_blocked=self.is_blocked(
                    form.cleaned_data['first_name'],
                    form.cleaned_data['last_name'],
                    form.cleaned_data['year_of_birth'],
                ),
            )
        )


class BlockListFileView(BlockListMixin, FormView):
    form_class = BlockListFileForm
    template_name = 'subjects/blocklist_file_form.html'

    def form_valid(self, form):
        try:
            data = self.request.FILES['file'].read().decode('utf-8')
        except UnicodeDecodeError:
            form.add_error('file', _('Uploaded file must be UTF-8 encoded.'))
            return self.form_invalid(form)

        r = csv.DictReader(StringIO(data))
        for key in ['first_name', 'last_name', 'year_of_birth']:
            if key not in r.fieldnames:
                form.add_error('file', _('Missing column: ') + key)
                return self.form_invalid(form)

        response = HttpResponse(content_type='text/csv')
        w = csv.DictWriter(response, fieldnames=[*r.fieldnames, 'is_blocked'])
        w.writeheader()

        for row in r:
            is_blocked = self.is_blocked(
                row['first_name'], row['last_name'], int(row['year_of_birth'], 10)
            )
            row['is_blocked'] = 'yes' if is_blocked else 'no'
            w.writerow(row)

        return response
