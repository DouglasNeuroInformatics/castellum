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

    var invited = document.querySelector('[name="status"] [value="3"]');
    var alert = document.querySelector('[data-js="blocking_invitation_alert"]');
    if (!invited.disabled) {
        var setInvitedDisabled = function() {
            var checked = document.querySelector('[name="exclusion_criteria_checked"]');
            var needsCheck = checked && !checked.checked;
            invited.disabled = needsCheck;
            if (alert) {
                alert.hidden = !needsCheck;
            }
        };

        $$.on(document, 'change', '[name="exclusion_criteria_checked"]', setInvitedDisabled);
        setInvitedDisabled();
    }

    $$.on(document, 'change', '[name="exclusion_criteria_checked"]', function() {
        document.querySelector('#criteria-tab .fa-exclamation-triangle').hidden = this.checked;
    });
})();
