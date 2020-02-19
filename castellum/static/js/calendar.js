$(function() {
    $('[data-js="calendar"]').each(function(i, el) {
        var calendar = new FullCalendar.Calendar(el, {
            plugins: ['dayGrid', 'timeGrid', 'bootstrap'],
            themeSystem: 'bootstrap',
            locale: $('html').attr('lang'),
            events: JSON.parse($('#events').text()),
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
