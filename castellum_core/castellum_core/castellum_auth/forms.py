from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserCreationAdminForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        if not self.cleaned_data["password1"]:
            self.cleaned_data["password1"] = None
        return super().save(commit=commit)
