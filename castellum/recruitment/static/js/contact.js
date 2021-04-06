(function() {
    var setVisibility = function() {
        var status = document.querySelector('[name="status"]');
        var followupInput = document.querySelector('[name="followup_date"]');
        var followup = followupInput.closest('.form-row');

        if (status.value === '4') {
            followup.hidden = false;
            followupInput.required = true;
        } else {
            followup.hidden = true;
            followupInput.required = false;
            followupInput.value = '';
        }
    };

    $$.on(document, 'change', '[name="status"]', setVisibility);
    setVisibility();

    var participating = document.querySelector('[name="status"] [value="3"]');
    var alert = document.querySelector('[data-js="blocking_invitation_alert"]');
    if (!participating.disabled) {
        var setParticipatingDisabled = function() {
            var checked = document.querySelector('[name="exclusion_criteria_checked"]');
            var needsCheck = checked && !checked.checked;
            participating.disabled = needsCheck;
            if (alert) {
                alert.hidden = !needsCheck;
            }
        };

        $$.on(document, 'change', '[name="exclusion_criteria_checked"]', setParticipatingDisabled);
        setParticipatingDisabled();
    }

    $$.on(document, 'change', '[name="exclusion_criteria_checked"]', function() {
        document.querySelector('#criteria-tab .fa-exclamation-triangle').hidden = this.checked;
    });

    if (document.querySelector('#appointments .is-invalid')) {
        $('#appointments-tab').tab('show');
    }
})();
