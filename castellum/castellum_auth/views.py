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
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.translation import check_for_language

from fido2 import cbor
from fido2.client import ClientData
from fido2.ctap2 import AttestationObject
from fido2.ctap2 import AttestedCredentialData
from fido2.ctap2 import AuthenticatorData
from fido2.server import Fido2Server
from fido2.utils import websafe_decode
from fido2.utils import websafe_encode
from fido2.webauthn import PublicKeyCredentialRpEntity

from castellum.utils.views import get_next_url

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


def get_credentials(user):
    raw = user.fido2_credential_data
    if not raw:
        raise Http404
    return [AttestedCredentialData(websafe_decode(raw)))]


def register_begin(request):
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


def register_complete(request):
    data = cbor.decode(request.body)

    auth_data = fido2.register_complete(
        request.session.pop('fido2_state'),
        ClientData(data['clientData']),
        AttestationObject(data['attestationObject']),
    )

    request.user.fido2_credential_data = websafe_encode(auth_data.credential_data)
    request.user.save()

    return HttpResponse()


def authenticate_begin(request):
    auth_data, state = fido2.authenticate_begin(get_credentials(request.user))
    request.session['fido2_state'] = state
    return HttpResponse(cbor.encode(auth_data), content_type='application/cbor')


def authenticate_complete(request):
    data = cbor.decode(request.body)

    fido2.authenticate_complete(
        request.session.pop('fido2_state'),
        get_credentials(request.user),
        data['credentialId'],
        ClientData(data['clientData']),
        AuthenticatorData(data['authenticatorData']),
        data['signature'],
    )

    return HttpResponse()
