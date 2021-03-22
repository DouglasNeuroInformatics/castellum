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

import codecs
import json
from typing import Any
from typing import Mapping

from django import forms
from django.forms import ValidationError
from django.forms.widgets import TextInput
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

import jsonschema
import magic
from phonenumber_field.formfields import PhoneNumberField as _PhoneNumberFormField
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


class ColorInput(forms.TextInput):
    input_type = 'color'


class AdminColorInputWidget(ColorInput):
    def __init__(self, attrs=None):
        super().__init__(attrs={'class': 'vTextField', **(attrs or {})})


class DateInput(forms.DateInput):
    def __init__(self, attrs=None):
        defaults = {
            'placeholder': _('yyyy-mm-dd, e.g. 2018-07-21'),
            'autocomplete': 'off',
            'type': 'date',
        }
        if attrs:
            defaults.update(attrs)
        super().__init__(format='%Y-%m-%d', attrs=defaults)


class DateTimeInput(forms.SplitDateTimeWidget):
    template_name = 'utils/widgets/splitdatetime.html'

    def __init__(self, date_attrs=None, time_attrs=None):
        date_defaults = {
            'placeholder': _('yyyy-mm-dd, e.g. 2018-07-21'),
            'autocomplete': 'off',
            'type': 'date',
        }
        if date_attrs:
            date_defaults.update(date_attrs)

        time_defaults = {
            'placeholder': _('HH:MM, e.g. 13:00'),
        }
        if time_attrs:
            time_defaults.update(time_attrs)

        super().__init__(date_format='%Y-%m-%d', date_attrs=date_defaults, time_attrs=time_defaults)


class ColorField(forms.CharField):
    widget = ColorInput


class DateField(forms.DateField):
    widget = DateInput


class DateTimeField(forms.SplitDateTimeField):
    widget = DateTimeInput


class PhoneNumberWidget(PhoneNumberInternationalFallbackWidget):
    def __init__(self, attrs=None):
        defaults = {
            'placeholder': _('e.g. 030 123456'),
        }
        if attrs:
            defaults.update(defaults)
        super().__init__(attrs=defaults)


class PhoneNumberField(_PhoneNumberFormField):
    widget = PhoneNumberWidget


class DisabledSelect(forms.Select):
    def __init__(self, **kwargs):
        self.disabled_choices = kwargs.pop('disabled_choices', [])
        super().__init__(**kwargs)

    def create_option(self, name, value, *args, **kwargs):
        option = super().create_option(name, value, *args, **kwargs)
        if value in self.disabled_choices:
            option['attrs']['disabled'] = True
        return option


class DisabledChoiceField(forms.TypedChoiceField):
    widget = DisabledSelect

    def validate(self, value):
        if value in self.widget.disabled_choices:
            raise forms.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        return super().validate(value)


class DisabledModelChoiceField(forms.ModelChoiceField):
    widget = DisabledSelect

    def validate(self, value):
        # value is the instance, so we have to check value.pk
        if value.pk in self.widget.disabled_choices:
            raise forms.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )
        return super().validate(value)


class IntegerChoiceField(forms.TypedChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('coerce', int)
        super().__init__(*args, **kwargs)


class IntegerMultipleChoiceField(forms.TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('coerce', int)
        super().__init__(*args, **kwargs)


class DatalistWidget(TextInput):
    template_name = 'utils/widgets/datalist.html'

    def __init__(self, *args, datalist=[], **kwargs):
        self.datalist = datalist
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['list'] = context['widget']['attrs']['id'] + '_list'
        context['datalist'] = self.datalist
        return context


class RestrictedFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', [])
        self.max_upload_size = kwargs.pop('max_upload_size', 0)
        super().__init__(*args, **kwargs)

    def to_python(self, data):
        f = super().to_python(data)
        if f is None:
            return None

        if self.max_upload_size and f.size > self.max_upload_size:
            raise forms.ValidationError(_('File is too big.'), code='size')

        content_type = magic.detect_from_content(f.read(1024)).mime_type
        if content_type not in self.content_types:
            raise forms.ValidationError(_('Filetype not supported.'), code='content_type')

        f.seek(0)

        return f

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if self.content_types:
            attrs.setdefault('accept', ','.join(self.content_types))
        return attrs


@deconstructible
class JsonFileValidator:
    def __init__(self, schema, schema_ref):
        self.schema = {'$ref': schema_ref}
        self.schema.update(schema)

    def format_error(self, error):
        path = '.'.join(str(x) for x in error.path)
        return '{} {}'.format(path, error.message)

    def __eq__(self, other):
        return self.schema == other.schema

    def __call__(self, fh):
        try:
            reader = codecs.getreader('utf-8')
            data = json.load(reader(fh))
        except json.JSONDecodeError:
            raise ValidationError(_('Uploaded file does not contain valid JSON.'), code='encoding')
        except UnicodeDecodeError:
            raise ValidationError(_('Uploaded file must be UTF-8 encoded.'), code='json')

        validator = jsonschema.Draft7Validator(self.schema)
        errors = list(validator.iter_errors(data))
        if errors:
            raise ValidationError([
                ValidationError(self.format_error(error), code='schema') for error in errors
            ])

        return data


class BaseImportForm(forms.Form):
    schema: Mapping[str, Any]
    schema_ref: str

    # magic seems to detect 'text/plain' for json files
    file = RestrictedFileField(
        label=_('File'), content_types=['application/json', 'text/plain'], required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        if 'file' in cleaned_data:
            validator = JsonFileValidator(self.schema, self.schema_ref)
            cleaned_data['json'] = validator(cleaned_data['file'])
        return cleaned_data


class TagField(forms.MultipleChoiceField):
    def valid_value(self, value):
        return True

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs['data-js'] = 'select2-tags'
        return attrs
