$(function() {
    var submitted = false;

    var registerBeforeUnload = function() {
        $(window).on('beforeunload', function(event) {
            if (!submitted) {
                event.preventDefault();
                // Chrome requires returnValue to be set.
                event.returnValue = '';
            }
        });
    };

    $('[data-js="unsaved-changes"]')
    .on('change', registerBeforeUnload)
    .on('submit', function(event) {
        submitted = true;
    });
});
