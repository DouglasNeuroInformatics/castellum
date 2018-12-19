$(function() {
    $('[data-widget="datepicker"]').each(function(i, e) {
        e.type = 'date';
        if (e.type !== 'date') {
            $(e).datepicker({
                format: django.formats.DATE_INPUT_FORMATS[0]
                    .replace('%Y', 'yyyy')
                    .replace('%m', 'mm')
                    .replace('%d', 'dd'),
                language: document.documentElement.lang,
                autoclose: true,
                calendarWeeks: true,
                daysOfWeekHighlighted: "0,6",
                todayHighlight: true,
            });
        }
    });
});
