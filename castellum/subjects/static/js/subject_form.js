$(function() {
    var $consent = $('[name="consent_status"]');
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
        } else if (value === '') {
            $consentCheckbox.prop('indeterminate', false);
            $consentCheckbox.prop('checked', false);
            $consentConfirm.prop('hidden', true);
        }
        $consent.val(value);
    };
    $consentCheckbox.on('change', function() {
        setConsent($consent.val() ? '' : 'waiting');
    });
    $consentConfirm.on('click', function() {
        setConsent('confirmed');
    });

    // initialize
    setConsent($consent.val());
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
