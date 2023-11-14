var unsavedForms = [];

var registerBeforeUnload = function() {
    window.addEventListener('beforeunload', function(event) {
        if (unsavedForms.length) {
            event.preventDefault();
            // Chrome requires returnValue to be set.
            event.returnValue = '';
            return event.returnValue;
        }
    });
};

document.addEventListener('change', function(event) {
    // form can be defined implicitly (ancestor) or explicitly (`form="…"`)
    var form = event.target.form;
    if (!form || form.method.toLowerCase() !== 'post') {
        return;
    }

    // beforeunload prevents caching, so only register it when necessary
    registerBeforeUnload();
    if (!unsavedForms.includes(form)) {
        unsavedForms.push(form);
    }
});
$$.on(document, 'submit', 'form', function() {
    unsavedForms = unsavedForms.filter(f => f !== this);
});

$$.on(document, 'click', '[data-js="cancel"]', function() {
    unsavedForms = [];
});
