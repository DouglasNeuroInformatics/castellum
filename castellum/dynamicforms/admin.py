from django.contrib import admin

from .example import MyDynamicFormField
from .example import MyDynamicModel

admin.site.register(MyDynamicFormField)
admin.site.register(MyDynamicModel)
