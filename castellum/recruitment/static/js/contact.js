var status = document.querySelector('[name="status"]');
var followupInput = document.querySelector('[name="followup_date"]');
var followupTimeInput = document.querySelector('[name="followup_time"]');
var followup = followupInput.closest('.row');

// https://bugs.webkit.org/show_bug.cgi?id=275612
var min = followupInput.min;

var setVisibility = function() {
    if (status.value === '4') {
        followup.hidden = false;
        followupInput.required = true;
        followupInput.min = min;
    } else {
        followup.hidden = true;
        followupInput.required = false;
        followupInput.value = '';
        followupInput.min = '';
        followupTimeInput.value = '';
    }
};

$$.on(document, 'change', '[name="status"]', setVisibility);
setVisibility();
