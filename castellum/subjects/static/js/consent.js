(function() {
    var consentHidden = document.getElementById('id_consent_status_hidden');
    var consentCheckbox = document.getElementById('id_consent_status');
    var consentConfirm = document.querySelector('[data-js="consent-confirm"]');

    var setConsent = function(value) {
        if (value === 'waiting') {
            consentCheckbox.indeterminate = true;
            consentCheckbox.checked = false;
            consentConfirm.hidden = false;
        } else if (value === 'confirmed') {
            consentCheckbox.indeterminate = false;
            consentCheckbox.checked = true;
            consentConfirm.hidden = true;
        } else {
            consentCheckbox.indeterminate = false;
            consentCheckbox.checked = false;
            consentConfirm.hidden = true;
        }
        if (value !== consentHidden.value) {
            consentHidden.value = value;
            $$.trigger(consentHidden, 'change');
        }
    };

    $$.on(document, 'change', '#id_consent_status', function() {
        setConsent(consentHidden.value ? '' : 'waiting');
    });
    $$.on(document, 'click', '[data-js="consent-confirm"] button', function() {
        setConsent('confirmed');
        consentCheckbox.focus();
    });
    setConsent(consentHidden.value);


    var oldConsentValue = consentHidden.value;
    $$.on(document, 'change', '#id_to_be_deleted', function() {
        if (this.checked) {
            oldConsentValue = consentHidden.value;
            setConsent('');
            consentCheckbox.disabled = true;
        } else {
            setConsent(oldConsentValue);
            consentCheckbox.disabled = false;
        }
    });

    // only enable dummy checkbox when everything is set up
    if (!document.getElementById('id_to_be_deleted').checked) {
        consentCheckbox.disabled = false;
    }
})();
