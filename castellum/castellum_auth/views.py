# (c) 2018-2021
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
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
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import check_for_language
from django.views.generic import View

from fido2 import cbor
from fido2.client import ClientData
from fido2.ctap2 import AttestationObject
from fido2.ctap2 import AttestedCredentialData
from fido2.ctap2 import AuthenticatorData
from fido2.server import Fido2Server
from fido2.utils import websafe_decode
from fido2.utils import websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity
from stronghold.views import StrongholdPublicMixin

from castellum.utils.views import get_next_url

from .models import User

LANGUAGE_QUERY_PARAMETER = 'language'

fido2 = Fido2Server(PublicKeyCredentialRpEntity(settings.DOMAIN, settings.SITE_TITLE))


def set_language(request):
    """Save language in the user model.

    See also django.views.i18n.set_language
    """
    if request.method == 'POST' and request.user.is_authenticated:
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            request.user.language = lang_code
            request.user.save()

    return redirect(get_next_url(request))


class LoginView(DjangoLoginView):
    def form_valid(self, form):
        if settings.CASTELLUM_REQUIRE_FIDO2:
            user = form.get_user()
            self.request.session['fido2_user'] = {
                'pk': user.pk,
                'backend': user.backend,
            }
            return self.render_to_response(self.get_context_data(
                fido2_required=True,
                success_url=self.get_success_url(),
            ))
        else:
            return super().form_valid(form)


def get_credentials(user):
    raw = user.fido2_credential_data
    if not raw:
        raise Http404
    return [AttestedCredentialData(websafe_decode(raw))]


class FIDO2RegisterView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        registration_data, state = fido2.register_begin(
            {
                'id': str(request.user.id).encode('utf-8'),
                'name': request.user.username,
                'displayName': request.user.get_full_name(),
            },
            [],
        )
        request.session['fido2_state'] = state
        return HttpResponse(cbor.encode(registration_data), content_type='application/cbor')

    def post(self, request, *args, **kwargs):
        data = cbor.decode(request.body)

        auth_data = fido2.register_complete(
            request.session.pop('fido2_state'),
            ClientData(data['clientData']),
            AttestationObject(data['attestationObject']),
        )

        request.user.fido2_credential_data = websafe_encode(auth_data.credential_data)
        request.user.save()

        return HttpResponse()


class FIDO2AuhenticateView(StrongholdPublicMixin, View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.session['fido2_user']['pk'])

        auth_data, state = fido2.authenticate_begin(get_credentials(user))
        request.session['fido2_state'] = state
        return HttpResponse(cbor.encode(auth_data), content_type='application/cbor')

    def post(self, request, *args, **kwargs):
        user_data = request.session.pop('fido2_user')
        user = User.objects.get(pk=user_data['pk'])
        user.backend = user_data['backend']

        data = cbor.decode(request.body)

        fido2.authenticate_complete(
            request.session.pop('fido2_state'),
            get_credentials(user),
            data['credentialId'],
            ClientData(data['clientData']),
            AuthenticatorData(data['authenticatorData']),
            data['signature'],
        )
        login(request, user)

        return HttpResponse()
