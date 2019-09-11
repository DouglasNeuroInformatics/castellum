$(function() {
    $(document).on('submit', '[data-js="disable-on-submit"]', function() {
        $(this).find('[type="submit"]').prop('disabled', true);
    });
});
