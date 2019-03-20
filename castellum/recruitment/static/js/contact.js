$(function() {
    var setVisibility = function() {
        var $status = $('[name="status"]');
        var $appointmentInputs = $('[name^="appointment"]');
        var $appointment = $appointmentInputs.closest('.form-group');

        if ($status.val() === "4") {
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
});
