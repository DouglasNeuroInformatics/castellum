(function() {
    var $consentHidden = $('#id_consent_status_hidden');
    var $consentCheckbox = $('#id_consent_status');
    var $consentConfirm = $('[data-js="consent-confirm"]');

    var setConsent = function(value) {
        if (value === 'waiting') {
            $consentCheckbox.prop('indeterminate', true);
            $consentCheckbox.prop('checked', false);
            $consentConfirm.prop('hidden', false);
        } else if (value === 'confirmed') {
            $consentCheckbox.prop('indeterminate', false);
            $consentCheckbox.prop('checked', true);
            $consentConfirm.prop('hidden', true);
        } else {
            $consentCheckbox.prop('indeterminate', false);
            $consentCheckbox.prop('checked', false);
            $consentConfirm.prop('hidden', true);
        }
        if (value !== $consentHidden.val()) {
            $consentHidden.val(value);
            $consentHidden.trigger('change');
        }
    };

    $consentCheckbox.on('change', function() {
        setConsent($consentHidden.val() ? '' : 'waiting');
    });
    $consentConfirm.on('click', 'button', function() {
        setConsent('confirmed');
    });
    setConsent($consentHidden.val());


    var $toBeDeleted = $('#id_to_be_deleted');
    var oldConsentValue = $consentHidden.val();
    $toBeDeleted.on('change', function() {
        if ($toBeDeleted.prop('checked')) {
            oldConsentValue = $consentHidden.val();
            setConsent('');
            $consentCheckbox.prop('disabled', true);
        } else {
            setConsent(oldConsentValue);
            $consentCheckbox.prop('disabled', false);
        }
    });
})();
