$(function() {
    $('[data-js="calendar"]').each(function(i, el) {
        var calendar = new FullCalendar.Calendar(el, {
            plugins: ['dayGrid', 'timeGrid', 'bootstrap'],
            themeSystem: 'bootstrap',
            locale: $('html').attr('lang'),
            height: 'auto',
            header: {
                left: 'timeGridWeek,dayGridMonth',
                center: 'title',
                right: 'prev,next',
            },
            defaultView: 'timeGridWeek',
            views: {
                timeGridWeek: {
                    allDaySlot: false,
                    slotDuration: '01:00:00',
                },
            },
        });
        calendar.render();
    });
});
