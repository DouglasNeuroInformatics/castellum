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

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from .forms import DescriptionImportForm
from .models import AttributeCategory
from .models import AttributeChoice
from .models import AttributeDescription
from .models import MailBatch
from .models import NewsMailBatch
from .models import Participation
from .models import SubjectFilter
from .models import SubjectFilterGroup


class DescriptionImportView(PermissionRequiredMixin, FormView):
    template_name = 'admin/recruitment/attributedescription_import.html'
    permission_required = [
        'recruitment.view_attributedescription',
        'recruitment.add_attributedescription',
    ]
    schema_ref = '#/definitions/AttributeDescriptionExport'
    model = AttributeDescription
    form_class = DescriptionImportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opts'] = self.model._meta
        context['title'] = _('Import')
        return context

    def form_valid(self, form):
        json = form.cleaned_data['json']
        for data in json['descriptions']:
            AttributeDescription._import(data)
        messages.success(
            self.request,
            _('Successfully imported %i attribute descriptions.' % len(json['descriptions']))
        )
        return self.form_invalid(form)


class AttributeChoiceInline(TranslatableTabularInline):
    model = AttributeChoice


class AttributeDescriptionAdmin(TranslatableAdmin):
    inlines = [
        AttributeChoiceInline,
    ]
    actions = ['export_json']

    def export_json(self, request, queryset):
        response = JsonResponse({
            'descriptions': [description.export() for description in queryset.all()],
        })
        response['Content-Disposition'] = 'attachment; filename="castellum_attributes.json"'
        return response
    export_json.short_description = _('Export as JSON')

    def get_urls(self):
        return [
            path(
                'import/',
                staff_member_required(DescriptionImportView.as_view()),
                name='recruitment_attributedescription_import',
            ),
        ] + super().get_urls()


admin.site.register(AttributeCategory, TranslatableAdmin)
admin.site.register(AttributeDescription, AttributeDescriptionAdmin)
admin.site.register(MailBatch)
admin.site.register(NewsMailBatch)
admin.site.register(Participation)
admin.site.register(SubjectFilter)
admin.site.register(SubjectFilterGroup)
