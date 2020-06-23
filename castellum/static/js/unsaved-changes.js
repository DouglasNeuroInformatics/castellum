(function() {
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

    $$.on(document, 'click', 'a:not([data-js="cancel"]):not([href^="#"])', function(event){
        if (unsavedForms.length) {
            event.preventDefault();
            var modal = document.querySelector('#unsaved-changes-modal');
            modal.querySelector('[data-js="cancel"]').href = this.href;
            $(modal).modal('show');
        }
    });

    $$.on(document, 'change', 'form[method="post"]', function() {
        // beforeunload prevents caching, so only register it when necessary
        registerBeforeUnload();
        if (!unsavedForms.includes(this)) {
            unsavedForms.push(this);
        }
    });
    $$.on(document, 'submit', 'form', function() {
        unsavedForms = unsavedForms.filter(f => f !== this);
    });

    $$.on(document, 'click', '[data-js="cancel"]', function() {
        unsavedForms = [];
    });
})();
