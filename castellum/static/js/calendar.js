document.querySelectorAll('[data-js="calendar"]').forEach(function(el) {
    var layout = el.dataset.layout;
    var calendar = new FullCalendar.Calendar(el, {
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        plugins: ['dayGrid', 'timeGrid', 'bootstrap', 'timeline'],
        themeSystem: 'bootstrap',
        locale: document.documentElement.lang,
        events: location.search ? (location.search + '&events') : '?events',
        eventSourceSuccess: function(raw) {
            return raw.events;
        },
        height: function() {
            var offsetTop = el.getBoundingClientRect().top + window.scrollY;
            return window.innerHeight - offsetTop - parseInt(getComputedStyle(el).marginBottom, 10);
        },
        header: {
            left: layout === 'year' ? 'timelineMonth,timelineYear' : 'timeGridWeek,dayGridMonth',
            center: 'title',
            right: 'prev,next',
        },
        defaultView: layout === 'year' ? 'timelineMonth' : 'timeGridWeek',
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
    setInterval(function() {
        calendar.refetchEvents();
    }, 5000);
    calendar.render();
});
