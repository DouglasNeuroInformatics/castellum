(function() {
    var setVisibility = function() {
        var status = document.querySelector('[name="status"]');
        var followupInput = document.querySelector('[name="followup_date"]');
        var followupTimeInput = document.querySelector('[name="followup_time"]');
        var followup = followupInput.closest('.row gx-2');

        if (status.value === '4') {
            followup.hidden = false;
            followupInput.required = true;
        } else {
            followup.hidden = true;
            followupInput.required = false;
            followupInput.value = '';
            followupTimeInput.value = '';
        }
    };

    $$.on(document, 'change', '[name="status"]', setVisibility);
    setVisibility();
})();
