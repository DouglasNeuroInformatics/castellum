$(function() {
    var setVisibility = function() {
        var $status = $('[name="status"]');
        var $appointmentInputs = $('[name^="appointment"]');
        var $appointment = $appointmentInputs.closest('.form-group');

        if ($status.val() === '4') {
            $appointment.prop('hidden', false);
            $appointmentInputs.prop('required', true);
        } else {
            $appointment.prop('hidden', true);
            $appointmentInputs.prop('required', false);
            $appointmentInputs.val('');
        }
    };

    $(document).on('change', '[name="status"]', setVisibility);
    setVisibility();

    var $invited = $('[name="status"] [value="3"]');
    if (!$invited.prop('disabled')) {
        var setInvitedDisabled = function() {
            var $checked = $('[name="exclusion_criteria_checked"]');
            if ($checked.length) {
                $invited.prop('disabled', !$checked.prop('checked'));
            }
        };

        $(document).on('change', '[name="exclusion_criteria_checked"]', setInvitedDisabled);
        setInvitedDisabled();
    }

    $(document).on('change', '[name="exclusion_criteria_checked"]', function() {
        $('#criteria-tab .fa-exclamation-triangle').prop('hidden', this.checked);
    });
});
