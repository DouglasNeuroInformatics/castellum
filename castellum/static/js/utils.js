$(function() {
    $(document).on('submit', '[data-js="disable-on-submit"]', function() {
        $(this).find('[type="submit"]').prop('disabled', true);
    });

    $(document).on('change', '[data-js="confirm-delete"]', function() {
        $(this.form).find('[type="submit"]').prop('disabled', !this.checked);
    });

    $('[type="date"]').each(function(i, e) {
        if (e.type !== 'date') {
            $(e).datepicker({
                format: 'yyyy-mm-dd',
                language: document.documentElement.lang,
                autoclose: true,
                calendarWeeks: true,
                daysOfWeekHighlighted: '0,6',
                todayHighlight: true,
            });
        }
    });
});
