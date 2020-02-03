$(function() {
    var submitted = false;

    var registerBeforeUnload = function() {
        $(window).on('beforeunload', function(event) {
            if (!submitted) {
                event.preventDefault();
                // Chrome requires returnValue to be set.
                event.returnValue = '';
                return event.returnValue;
            }
        });
    };

    // beforeunload prevents caching, so only register it when necessary
    $('form')
    .on('change', registerBeforeUnload)
    .on('submit', function() {
        submitted = true;
    });

    $(document).on('click', '[data-js="cancel"]', function() {
        submitted = true;
    });
});
