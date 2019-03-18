onReady(function() {
    var setVisibility = function() {
        var $status = document.querySelector('[name="status"]');
        var $appointmentInputs = document.querySelectorAll('[name^="appointment"]');
        var $appointment = $appointmentInputs[0].closest('.form-group');

        if ($status.value === "4") {
            $appointment.hidden = false;
            $appointmentInputs.forEach(function($e) {
                $e.required = true;
            });
        } else {
            $appointment.hidden = true;
            $appointmentInputs.forEach(function($e) {
                $e.required = false;
                $e.value = '';
            });
        }
    };

    on(document, 'change', '[name="status"]', setVisibility);
    setVisibility();
});
