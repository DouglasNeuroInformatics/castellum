$(function() {
    $(document).on('click', '[data-js="delete"]', function(event) {
        var msg = django.gettext('Are you sure you want to delete this entry?');
        if (!confirm(msg)) {
            event.preventDefault();
        }
    });

    $('[data-js="unsaved-changes"]').each(function(i, el) {
        var submitted = false;

        $(el).one('change', function() {
            $(window).on('beforeunload', function(event) {
                if (!submitted) {
                    event.preventDefault();
                    // Chrome requires returnValue to be set.
                    event.returnValue = '';
                }
            });
        }).on('submit', function(event) {
            submitted = true;
        });
    });
});
