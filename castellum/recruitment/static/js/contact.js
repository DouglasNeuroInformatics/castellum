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
})();
