$(function() {
    $(document).on('click', '[data-js="delete"]', function(event) {
        var msg = django.gettext('Are you sure you want to delete this entry?');
        if (!confirm(msg)) {
            event.preventDefault();
        }
    });
});
