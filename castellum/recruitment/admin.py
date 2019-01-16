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

import json

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.urls import path
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from castellum.castellum_auth.mixins import PermissionRequiredMixin

from .models import AttributeChoice
from .models import AttributeDescription
from .models import AttributeSet
from .models import ParticipationRequest
from .models import ParticipationRequestRevision
from .models import SubjectFilter
from .models import SubjectFilterGroup


class ImportView(PermissionRequiredMixin, TemplateView):
    template_name = 'admin/recruitment/attributedescription_import.html'
    permission_required = ['recruitment.view_attributeset', 'recruitment.add_attributeset']

    def get_context_data(self):
        context = super().get_context_data()
        context['opts'] = AttributeDescription._meta
        return context

    def get_items(self):
        fh = self.request.FILES['file']
        if not fh:
            return
        try:
            return json.load(fh)['descriptions']
        except (json.JSONDecodeError, UnicodeDecodeError):
            messages.error(self.request, _('Uploaded file does not contain valid JSON.'))

    def get_forms(self, items):
        form_cls = modelform_factory(AttributeDescription, fields='__all__')

        translation_model = AttributeDescription._parler_meta.root_model
        translation_form_cls = modelform_factory(translation_model, exclude=['language_code'])

        choice_translation_model = AttributeChoice._parler_meta.root_model
        choice_translation_form_cls = modelform_factory(
            choice_translation_model, exclude=['language_code'])

        return [(
            form_cls(item), {
                lang: translation_form_cls(translation)
                for lang, translation in item.get('translations', {}).items()
            }, [
                {
                    lang: choice_translation_form_cls(translation)
                    for lang, translation in choice.get('translations').items()
                }
                for choice in item.get('choices', [])
            ],
        ) for item in items]

    def is_valid(self, forms):
        return all(
            form.is_valid()
            and all(form.is_valid() for form in translation_forms.values())
            and all(all(form.is_valid() for form in choice.values()) for choice in choices)
            for form, translation_forms, choices in forms
        )

    def get_errors(self, forms):
        errors = {}
        for i, (form, translation_forms, choices) in enumerate(forms):
            for field, msg in form.errors.items():
                errors['item %i: %s' % (i, field)] = msg

            for lang, translation_form in translation_forms.items():
                for field, msg in translation_form.errors.items():
                    errors['item %i: translations[%s].%s' % (i, lang, field)] = msg

            for j, choice in enumerate(choices):
                for lang, choice_form in choice.items():
                    for field, msg in choice_form.errors.items():
                        key = 'item %i: choice[%i].translations[%s].%s' % (i, j, lang, field)
                        errors[key] = msg
        return errors

    def post(self, request, *args, **kwargs):
        items = self.get_items()
        forms = []
        if items:
            forms = self.get_forms(items)
            if self.is_valid(forms):
                for form, translation_forms, choices in forms:
                    instance = form.save()
                    for lang, translation_form in translation_forms.items():
                        translation_form.instance.language_code = lang
                        translation_form.instance.master = instance
                        translation_form.save()
                    for choice in choices:
                        choice_instance = AttributeChoice.objects.create(description=instance)
                        for lang, choice_form in choice.items():
                            choice_form.instance.language_code = lang
                            choice_form.instance.master = choice_instance
                            choice_form.save()
                messages.success(
                    self.request,
                    _('Successfully imported %i attribute descriptions.' % len(forms)))

        context = self.get_context_data()
        context['errors'] = self.get_errors(forms)
        return self.render_to_response(context)


class AttributeChoiceInline(TranslatableTabularInline):
    model = AttributeChoice


class AttributeDescriptionAdmin(TranslatableAdmin):
    inlines = [
        AttributeChoiceInline,
    ]
    actions = ['export_json']

    def export_json(self, request, queryset):
        return JsonResponse({
            'descriptions': [description.export() for description in queryset.all()],
        })
    export_json.short_description = _('Export as JSON')

    def get_urls(self):
        return [
            path(
                'import/',
                staff_member_required(ImportView.as_view()),
                name='recruitment_attributedescription_import'),
        ] + super().get_urls()


admin.site.register(AttributeDescription, AttributeDescriptionAdmin)
admin.site.register(AttributeSet)
admin.site.register(ParticipationRequest)
admin.site.register(ParticipationRequestRevision)
admin.site.register(SubjectFilter)
admin.site.register(SubjectFilterGroup)
