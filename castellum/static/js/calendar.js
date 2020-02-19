$(function() {
    $('[data-js="calendar"]').each(function(i, el) {
        var calendar = new FullCalendar.Calendar(el, {
            plugins: ['dayGrid', 'timeGrid', 'bootstrap'],
            themeSystem: 'bootstrap',
            locale: $('html').attr('lang'),
            height: function() {
                return $(window).height() - $(el).offset().top - parseInt($(el).css('margin-bottom'), 10);
            },
            header: {
                left: 'timeGridWeek,dayGridMonth',
                center: 'title',
                right: 'prev,next',
            },
            defaultView: 'timeGridWeek',
            views: {
                timeGridWeek: {
                    allDaySlot: false,
                    slotDuration: '00:30:00',
                    scrollTime: '08:00:00',
                },
            },
        });
        setInterval(function() {
            calendar.refetchEvents();
        }, 5000);
        calendar.render();
    });
});
