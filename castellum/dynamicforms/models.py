from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DynamicFormField(models.Model):
    TYPE_CHOICES = (
        ('CharField', _('CharField')),
        ('IntegerField', _('IntegerField')),
        ('DateField', _('DateField')),
    )

    TYPE_MAPPING = {
        'CharField': forms.CharField,
        'IntegerField': forms.IntegerField,
        'DateField': forms.DateField,
    }

    label = models.CharField(_('label'), max_length=64)
    help_text = models.TextField(_('help text'), blank=True)
    required = models.BooleanField(_('required'), default=True)
    field_type = models.CharField(_('field type'), max_length=64, choices=TYPE_CHOICES)

    class Meta:
        abstract = True

    def __str__(self):
        return self.label

    @property
    def name(self):
        # can not be a number because then queries like `data__8` would expect an array.
        return 'd{}'.format(self.pk)

    def get_form_field(self):
        form_class = self.TYPE_MAPPING[self.field_type]
        return form_class(
            label=self.label,
            help_text=self.help_text,
            required=self.required,
        )
