from django import forms
from django.views.generic import UpdateView


class DynamicModelForm(forms.Form):
    dynamic_field = 'data'

    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        if not kwargs.get('initial'):
            kwargs['initial'] = getattr(instance, self.dynamic_field)
        super().__init__(**kwargs)

    def save(self):
        setattr(self.instance, self.dynamic_field, self.cleaned_data)
        self.instance.save()
        return self.instance


def dynamic_form_factory(queryset, form_class=forms.Form):
    fields = {field.name: field.get_form_field() for field in queryset}
    return type('DynamicForm', (form_class,), fields)


class DynamicUpdateView(UpdateView):
    form_class = DynamicModelForm
    dynamic_form_model = None

    def get_form_class(self):
        if not self.dynamic_form_model:
            raise Exception  # TODO: raise a more meaningful exception
        form_class = super().get_form_class()
        queryset = self.dynamic_form_model.objects.all()
        return dynamic_form_factory(queryset, form_class=form_class)
