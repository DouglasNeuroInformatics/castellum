$(function() {
    var unsavedForms = [];

    var registerBeforeUnload = function() {
        $(window).on('beforeunload', function(event) {
            if (unsavedForms.length) {
                event.preventDefault();
                // Chrome requires returnValue to be set.
                event.returnValue = '';
                return event.returnValue;
            }
        });
    };

    $(document).on('click', 'a:not([data-js="cancel"]):not([href^="#"]):not([data-js="popup"]):not([target])', function(event){
        if (unsavedForms.length) {
            event.preventDefault();
            var $modal = $('#unsaved-changes-modal');
            $modal.find('[data-js="cancel"]').prop('href', this.href);
            $modal.modal('show');
        }
    });

    $(document).on('change', 'form[method="post"]', function() {
        // beforeunload prevents caching, so only register it when necessary
        registerBeforeUnload();
        if (!unsavedForms.includes(this)) {
            unsavedForms.push(this);
        }
    });
    $(document).on('submit', 'form', function() {
        unsavedForms = unsavedForms.filter(f => f !== this);
    });

    $(document).on('click', '[data-js="cancel"]', function() {
        unsavedForms = [];
    });
});
