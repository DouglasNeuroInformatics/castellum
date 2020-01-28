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

    $(document).on('click', 'a', function(event){
        if (unsavedForms.length) {
            event.preventDefault();
            var $modal = $('#unsaved-changes-modal');
            $modal.find('[data-js="cancel"]').prop('href', this.href);
            $modal.modal('show');
        }
    });

    $(document).on('click', '[data-js="submit-unsaved"]', function() {
        // NOTE: We can only submit one form. Should be fine in most cases.
        var form = unsavedForms[0];
        unsavedForms = [];
        form.submit();
    });

    $(document).on('change', 'form', function() {
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
