(function() {
    var setVisibility = function() {
        var $status = $('[name="status"]');
        var $followupInputs = $('[name="followup_date"]');
        var $followup = $followupInputs.closest('.form-row');

        if ($status.val() === '4') {
            $followup.prop('hidden', false);
            $followupInputs.prop('required', true);
        } else {
            $followup.prop('hidden', true);
            $followupInputs.prop('required', false);
            $followupInputs.val('');
        }
    };

    $(document).on('change', '[name="status"]', setVisibility);
    setVisibility();

    var $invited = $('[name="status"] [value="3"]');
    var $alert = $('[data-js="blocking_invitation_alert"]');
    if (!$invited.prop('disabled')) {
        var setInvitedDisabled = function() {
            var $checked = $('[name="exclusion_criteria_checked"]');
            var needsCheck = $checked.length && !$checked.prop('checked');
            $invited.prop('disabled', needsCheck);
            $alert.prop('hidden', !needsCheck);
        };

        $(document).on('change', '[name="exclusion_criteria_checked"]', setInvitedDisabled);
        setInvitedDisabled();
    }

    $(document).on('change', '[name="exclusion_criteria_checked"]', function() {
        $('#criteria-tab .fa-exclamation-triangle').prop('hidden', this.checked);
    });

    if ($('#appointments .is-invalid').length) {
        $('#appointments-tab').tab('show');
    }

    var getDate = function(selector) {
        var s = $(selector).prop('dateTime');
        return s ? new Date(s) : null;
    };

    $(document).on('submit', 'form', function(event) {
        var start = getDate('#sessions-start');
        var end = getDate('#sessions-end');
        var warn = false;
        $('[name^="appointment"][type="date"]').each(function(i, el) {
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
