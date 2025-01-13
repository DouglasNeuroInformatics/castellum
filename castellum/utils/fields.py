# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField as _PhoneNumberField

from .forms import AdminColorInputWidget
from .forms import ColorField as ColorFormField
from .forms import DateField as DateFormField
from .forms import DateTimeField as DateTimeFormField
from .forms import PhoneNumberField as PhoneNumberFormField
from .forms import RestrictedFileField as RestrictedFileFormField


class ColorField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 7)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', ColorFormField)
        return super().formfield(**kwargs)


FORMFIELD_FOR_DBFIELD_DEFAULTS[ColorField] = {'widget': AdminColorInputWidget}


class DateField(models.DateField):
    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', DateFormField)
        return super().formfield(**kwargs)


class DateTimeField(models.DateTimeField):
    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', DateTimeFormField)
        return super().formfield(**kwargs)


class PhoneNumberField(_PhoneNumberField):
    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', PhoneNumberFormField)
        return super().formfield(**kwargs)


class RestrictedFileField(models.FileField):
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop('content_types', [])
        self.max_upload_size = kwargs.pop('max_upload_size', 0)
        super().__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', RestrictedFileFormField)
        return super().formfield(
            content_types=self.content_types,
            max_upload_size=self.max_upload_size,
            **kwargs,
        )
