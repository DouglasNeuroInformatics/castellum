$(function() {
    var $consentHidden = $('#id_consent_status_hidden');
    var $consentCheckbox = $('#id_consent_status');

    var setConsent = function(value) {
        if (value === 'confirmed') {
            $consentCheckbox.prop('checked', true);
        } else {
            $consentCheckbox.prop('checked', false);
        }
        $consentHidden.val(value);
    };

    $consentCheckbox.on('change', function() {
        setConsent($consentCheckbox.prop('checked') ? 'confirmed' : '');
    });
    setConsent($consentHidden.val());


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
