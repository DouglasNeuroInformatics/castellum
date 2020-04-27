$(function() {
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
        $consentHidden.val(value);
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


    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $notes_container = $('#notes-container');

    $(document).on('click', '[data-js="note-add"]', function() {
        var $template = $('#note-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $notes_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="note-delete"]', function(event) {
        var $delete = $('#' + event.target.id.slice(0, -6));
        $delete.val(event.target.checked ? '' : 'on');
    });
});
