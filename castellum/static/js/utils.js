$(function() {
    var submitDisabled = false;
    $(document).on('submit', 'form', function(event) {
        if (submitDisabled) {
            event.preventDefault();
        } else {
            submitDisabled = true;
            setTimeout(function() {
                submitDisabled = false;
            }, 1000);
        }
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

    $(document).on('click', '[data-multi-reset]', function(event) {
        var $target = $($(event.target).data('multi-reset'));
        $target.find('option').each(function(i, element) {
            $(element).prop('selected', false);
        });
    });
});
