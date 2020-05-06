$(function() {
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

    var needsAppointment = function() {
        var prefixes = $('[name^="appointment-"]').map(function(i, el) {
            return '#' + el.id.slice(0, -1);
        });
        for (var i = 0; i < prefixes.length; i++) {
            if ($(prefixes[i] + '0').val() && $(prefixes[i] + '1').val()) {
                return false;
            }
        }
        return prefixes.length !== 0;
    };

    var $invited = $('[name="status"] [value="3"]');
    if (!$invited.prop('disabled')) {
        var setInvitedDisabled = function() {
            var $checked = $('[name="exclusion_criteria_checked"]');
            var needsCheck = $checked.length && !$checked.prop('checked');
            $invited.prop('disabled', needsCheck || needsAppointment());
        };

        $(document).on('change', setInvitedDisabled);
        setInvitedDisabled();
    }

    $(document).on('change', '[name="exclusion_criteria_checked"]', function() {
        $('#criteria-tab .fa-exclamation-triangle').prop('hidden', this.checked);
    });
    $(document).on('change', '[name^="appointment-"]', function() {
        $('#appointments-tab .fa-exclamation-triangle').prop('hidden', !needsAppointment());
    });

    if ($('#appointments .is-invalid').length) {
        $('#appointments-tab').tab('show');
    }
});
