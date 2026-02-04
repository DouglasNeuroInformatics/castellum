# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import UserChangeForm

from .models import User
from .models import generate_token


class UserChangeAdminForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['token'].required = False

    def save(self, *args, **kwargs):
        if not self.instance.token:
            self.instance.token = generate_token()
        return super().save(*args, **kwargs)


class AuthenticationForm(BaseAuthenticationForm):
    """Block demo users in production setups.

    We want demo users in dev and demo setups. But in production they
    are a major security issue.

    Creating demo users is already blocked in production. As an
    additional safeguard, we block login with the demo password in case
    ``settings.PRODUCTION`` was set after the user had already been
    created.
    """

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        if settings.PRODUCTION and password == User.DEMO_PASSWORD:
            raise self.get_invalid_login_error()
        return cleaned_data
