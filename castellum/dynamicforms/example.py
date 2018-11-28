from django.contrib.postgres.fields import JSONField
from django.db import models

from .models import DynamicFormField
from .views import DynamicUpdateView


class MyDynamicFormField(DynamicFormField):
    pass


class MyDynamicModel(models.Model):
    data = JSONField()


class MyDynamicUpdateView(DynamicUpdateView):
    model = MyDynamicModel
    dynamic_form_model = MyDynamicFormField
