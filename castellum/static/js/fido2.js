(function() {
    var csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

    var raiseForStatus = function(response) {
        if (!response.ok) {
            throw new Error(response.statusText);
        } else {
            return response;
        }
    };

    var fromCBOR = function(response) {
        return Promise.resolve(response)
            .then(raiseForStatus)
            .then(response => response.arrayBuffer())
            .then(CBOR.decode);
    };

    var register = function() {
        return fetch('/fido2/register/', {credentials: 'same-origin'})
            .then(fromCBOR)
            .then(options => navigator.credentials.create(options))
            .then(attestation => fetch('/fido2/register/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'X-CSRFToken': csrfToken},
                body: CBOR.encode({
                  'attestationObject': new Uint8Array(attestation.response.attestationObject),
                  'clientData': new Uint8Array(attestation.response.clientDataJSON),
                }),
            }))
            .then(raiseForStatus)
            .catch(alert)
            .then(() => alert(django.gettext('second factor has been registered')));
    };

    var authenticate = function() {
        return fetch('/fido2/authenticate/', {credentials: 'same-origin'})
            .then(fromCBOR)
            .then(options => navigator.credentials.get(options))
            .then(assertion => fetch('/fido2/authenticate/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {'X-CSRFToken': csrfToken},
                body: CBOR.encode({
                  'credentialId': new Uint8Array(assertion.rawId),
                  'authenticatorData': new Uint8Array(assertion.response.authenticatorData),
                  'clientData': new Uint8Array(assertion.response.clientDataJSON),
                  'signature': new Uint8Array(assertion.response.signature),
                }),
            }))
            .then(raiseForStatus)
            .catch(alert);
    };

    $$.on(document, 'click', '[data-js="fido2-register"]', register);
    $$.on(document, 'click', '[data-js="fido2-authenticate"]', authenticate);

    var fido2Auto = document.querySelector('[data-js="fido2-auto"]');
    if (fido2Auto) {
        authenticate().then(() => {
            window.location = fido2Auto.dataset.successUrl;
        });
    }
})();
