$(function() {
    $('[data-js="calendar"]').each(function(i, el) {
        var calendar = new FullCalendar.Calendar(el, {
            themeSystem: 'bootstrap',
            locale: $('html').attr('lang'),
            events: '?events',
            eventSourceSuccess: function(raw) {
                return raw.events;
            },
            headerToolbar: {
                left: 'timeGridWeek,dayGridMonth',
                center: 'title',
                right: 'prev,next',
            },
            initialView: 'timeGridWeek',
            views: {
                timeGridWeek: {
                    allDaySlot: false,
                    slotDuration: '00:30:00',
                    scrollTime: '08:00:00',
                },
            },
        });
        $(window).on('resize', function() {
            var height = $(window).height() - $(el).offset().top - parseInt($(el).css('margin-bottom'), 10);
            calendar.setOption('height', height);
        });
        setInterval(function() {
            calendar.refetchEvents();
        }, 5000);
        calendar.render();
    });
});
