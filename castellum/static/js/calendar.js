document.querySelectorAll('[data-js="calendar"]').forEach(function(el) {
    var layout = el.dataset.layout;
    var calendar = new FullCalendar.Calendar(el, {
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        themeSystem: 'bootstrap',
        locale: document.documentElement.lang,
        events: location.search ? (location.search + '&events') : '?events',
        eventSourceSuccess: function(raw) {
            return raw.events;
        },
        headerToolbar: {
            left: layout === 'year' ? 'timelineMonth,timelineYear' : 'timeGridWeek,dayGridMonth,listMonth',
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
        eventDidMount: function(arg) {
            arg.el.title = arg.event.title;
        },
    });
    window.addEventListener('resize', function() {
        var offsetTop = el.getBoundingClientRect().top + window.scrollY;
        var height = window.innerHeight - offsetTop - parseInt(getComputedStyle(el).marginBottom, 10);
        calendar.setOption('height', height);
    });
    setInterval(function() {
        calendar.refetchEvents();
    }, 5000);
    calendar.render();
});
