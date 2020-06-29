$(function() {
    $('[data-js="calendar"]').each(function(i, el) {
        var layout = $(el).data('layout');
        var calendar = new FullCalendar.Calendar(el, {
            schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
            themeSystem: 'bootstrap',
            locale: $('html').attr('lang'),
            events: location.search ? (location.search + '&events') : '?events',
            eventSourceSuccess: function(raw) {
                return raw.events;
            },
            headerToolbar: {
                left: layout === 'year' ? 'timelineMonth,timelineYear' : 'timeGridWeek,dayGridMonth',
                center: 'title',
                right: 'prev,next',
            },
            initialView: layout === 'year' ? 'timelineMonth' : 'timeGridWeek',
            views: {
                timelineMonth: {
                    duration: {months: 1},
                    slotDuration: {days: 1},
                },
                timelineYear: {
                    duration: {years: 1},
                    slotDuration: {weeks: 1},
                },
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
