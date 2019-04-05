$(function() {
    $(document).on('submit', '[data-js="disable-on-submit"]', function(event) {
        $(this).find('[type="submit"]').prop('disabled', true);
    });
});
