$(function() {
    $('[data-widget="datepicker"]').datepicker({
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
});
