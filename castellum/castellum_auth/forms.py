# (c) 2018-2024 MPIB <https://www.mpib-berlin.mpg.de/>,
#     2018-2019 MPI-CBS <https://www.cbs.mpg.de/>,
#     2018-2019 MPIP <http://www.psych.mpg.de/>
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

from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm as BaseAuthenticationForm
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.forms import UserChangeForm

from .models import User
from .models import generate_token


class UserCreationAdminForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, *args, **kwargs):
        if not self.cleaned_data['password1']:
            self.cleaned_data['password1'] = None
        return super().save(*args, **kwargs)


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
