$(function() {
    $('[type="date"]').each(function(i, e) {
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
