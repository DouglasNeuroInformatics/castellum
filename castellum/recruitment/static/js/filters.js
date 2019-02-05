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
                    // NOTE: Most browsers will ignore the custom message and show their own instead.
                    var msg = django.gettext('If you leave this page changes you made will not be saved.');
                    event.returnValue = msg;
                    return msg;
                }
            });
        }).on('submit', function(event) {
            submitted = true;
        });
    });
});
