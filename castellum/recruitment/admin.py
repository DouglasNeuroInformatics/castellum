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

import codecs
import json

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

import jsonschema
from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from .models import AttributeCategory
from .models import AttributeChoice
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest
from .models import ParticipationRequestRevision
from .models import SubjectFilter
from .models import SubjectFilterGroup

EXPORT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-06/schema#",
    "definitions": {
        "AttributeDescriptionExport": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "descriptions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Description"
                    }
                }
            },
            "required": [
                "descriptions"
            ],
            "title": "AttributeDescriptionExport"
        },
        "AttributeCategoryExport": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "categories": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Category"
                    }
                }
            },
            "required": [
                "categories"
            ],
            "title": "AttributeCategoryExport"
        },
        "Category": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "order": {
                    "type": "integer"
                },
                "label": {
                    "$ref": "#/definitions/TranslatedString"
                },
                "descriptions": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Description"
                    }
                }
            },
        },
        "Description": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "field_type": {
                    "type": "string",
                    "enum": [
                        "CharField",
                        "ChoiceField",
                        "MultipleChoiceField",
                        "OrderedChoiceField",
                        "IntegerField",
                        "BooleanField",
                        "DateField",
                        "AgeField"
                    ]
                },
                "privacy_level_read": {
                    "type": "integer"
                },
                "privacy_level_write": {
                    "type": "integer"
                },
                "order": {
                    "type": "integer"
                },
                "label": {
                    "$ref": "#/definitions/TranslatedString"
                },
                "choices": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Choice"
                    }
                },
                "_filter_label": {
                    "$ref": "#/definitions/TranslatedString"
                },
                "help_text": {
                    "$ref": "#/definitions/TranslatedText"
                }
            },
            "required": [
                "field_type",
                "label"
            ],
            "title": "Description"
        },
        "Choice": {
            "type": "object",
            "properties": {
                "label": {
                    "$ref": "#/definitions/TranslatedString"
                }
            },
            "required": [
                "label"
            ],
            "title": "Choice"
        },
        "TranslatedString": {
            "type": "object",
            "additionalProperties": False,
            "patternProperties": {
                "..": {
                    "type": "string",
                    "maxLength": 64
                }
            },
            "title": "Label"
        },
        "TranslatedText": {
            "type": "object",
            "additionalProperties": False,
            "patternProperties": {
                "..": {
                    "type": "string"
                }
            },
            "title": "Label"
        }
    }
}


class BaseImportView(PermissionRequiredMixin, TemplateView):
    template_name = 'admin/recruitment/attributedescription_import.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opts'] = self.model._meta
        context['title'] = _('Import')
        return context

    def get_json(self):
        fh = self.request.FILES['file']

        if not fh:
            return
        try:
            reader = codecs.getreader("utf-8")
            return json.load(reader(fh))
        except json.JSONDecodeError:
            messages.error(self.request, _('Uploaded file does not contain valid JSON.'))
        except UnicodeDecodeError:
            messages.error(self.request, _('Uploaded file must be UTF-8 encoded.'))

    def post(self, request, *args, **kwargs):
        json = self.get_json()
        schema = {'$ref': self.schema_ref}
        schema.update(EXPORT_SCHEMA)
        validator = jsonschema.Draft4Validator(schema)
        context = self.get_context_data()
        context['errors'] = list(validator.iter_errors(json))
        if not context['errors']:
            self.json_valid(json)
        return self.render_to_response(context)


class CategoryImportView(BaseImportView):
    permission_required = [
        'recruitment.view_attributecategory',
        'recruitment.add_attributecategory',
    ]
    schema_ref = '#/definitions/AttributeCategoryExport'
    model = AttributeCategory

    def json_valid(self, json):
        for data in json['categories']:
            AttributeCategory._import(data)
        messages.success(
            self.request,
            _('Successfully imported %i attribute categories.' % len(json['categories'])))


class DescriptionImportView(BaseImportView):
    permission_required = [
        'recruitment.view_attributedescription',
        'recruitment.add_attributedescription',
    ]
    schema_ref = '#/definitions/AttributeDescriptionExport'
    model = AttributeDescription

    def json_valid(self, json):
        for data in json['descriptions']:
            AttributeDescription._import(data)
        messages.success(
            self.request,
            _('Successfully imported %i attribute descriptions.' % len(json['descriptions'])))


class AttributeCategoryAdmin(TranslatableAdmin):
    model = AttributeCategory
    actions = ['export_json']

    def export_json(self, request, queryset):
        response = JsonResponse({
            'categories': [category.export() for category in queryset.all()],
        })
        response['Content-Disposition'] = 'attachment; filename="castellum_categories.json"'
        return response
    export_json.short_description = _('Export as JSON')

    def get_urls(self):
        return [
            path(
                'import/',
                staff_member_required(CategoryImportView.as_view()),
                name='recruitment_attributecategory_import'),
        ] + super().get_urls()


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
                name='recruitment_attributedescription_import'),
        ] + super().get_urls()


admin.site.register(AttributeCategory, AttributeCategoryAdmin)
admin.site.register(AttributeDescription, AttributeDescriptionAdmin)
admin.site.register(AttributeSet)
admin.site.register(ParticipationRequest)
admin.site.register(ParticipationRequestRevision)
admin.site.register(SubjectFilter)
admin.site.register(SubjectFilterGroup)
