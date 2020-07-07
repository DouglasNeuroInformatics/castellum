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

    if (document.querySelector('#appointments .is-invalid')) {
        $('#appointments-tab').tab('show');
    }

    var getDate = function(selector) {
        var el = document.querySelector(selector);
        return (el && el.dateTime) ? new Date(el.dateTime) : null;
    };

    $$.on(document, 'submit', 'form', function(event) {
        var start = getDate('#sessions-start');
        var end = getDate('#sessions-end');
        var warn = false;
        document.querySelectorAll('[name^="appointment"][type="date"]').forEach(function(el) {
            if (el.value) {
                var date = new Date(el.value)
                if ((start && date < start) || (end && date > end)) {
                    warn = true;
                }
            }
        });
        if (warn && !confirm(django.gettext('Some of the appointments are outside of the planned time period. Do you want to save it anyway?'))) {
            event.preventDefault();
        }
    });
})();
