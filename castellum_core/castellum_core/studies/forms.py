from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Study


class StudyForm(forms.ModelForm):

    name = forms.ModelChoiceField(label=_('Name'),
                                  widget=forms.Select(attrs={'class': 'form-control'}),
                                  queryset=Study.objects.all(), required=False)

    class Meta:
        model = Study
        exclude = ['contact_person']
