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
    if (warn && !confirm(document.querySelector('#i18n-appointments').content.textContent)) {
        event.preventDefault();
    }
});
