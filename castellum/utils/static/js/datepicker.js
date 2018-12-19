$(function() {
    $('[data-widget="datepicker"]').each(function(i, e) {
        e.type = 'date';
        if (e.type !== 'date') {
            $(e).datepicker({
                format: 'yyyy-mm-dd',
                language: document.documentElement.lang,
                autoclose: true,
                calendarWeeks: true,
                daysOfWeekHighlighted: "0,6",
                todayHighlight: true,
            });
        }
    });
});
