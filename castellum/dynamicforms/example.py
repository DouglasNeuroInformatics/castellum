from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse

from .models import DynamicFormField
from .views import DynamicUpdateView


class MyDynamicFormField(DynamicFormField):
    pass


class MyDynamicModel(models.Model):
    data = JSONField()

    def get_absolute_url(self):
        return reverse('dynamic:update', args=[self.pk])


class MyDynamicUpdateView(DynamicUpdateView):
    model = MyDynamicModel
    dynamic_form_model = MyDynamicFormField
