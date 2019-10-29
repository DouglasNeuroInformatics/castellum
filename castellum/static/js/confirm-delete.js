$(function() {
    $(document).on('change', '[data-js="confirm-delete"]', function() {
        $(this.form).find('[type="submit"]').prop('disabled', !this.checked);
    });
});
