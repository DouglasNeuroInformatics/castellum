FullCalendar.Bootstrap5.Internal.BootstrapTheme.prototype.baseIconClass = 'fa';
FullCalendar.Bootstrap5.Internal.BootstrapTheme.prototype.iconClasses = {
    close: 'fa-times',
    prev: 'fa-chevron-left',
    next: 'fa-chevron-right',
    prevYear: 'fa-angle-double-left',
    nextYear: 'fa-angle-double-right',
};
FullCalendar.Bootstrap5.Internal.BootstrapTheme.prototype.rtlIconClasses = {
    prev: 'fa-chevron-right',
    next: 'fa-chevron-left',
    prevYear: 'fa-angle-double-right',
    nextYear: 'fa-angle-double-left',
};

document.querySelectorAll('[data-js="calendar"]').forEach(function(el) {
    var layout = el.dataset.layout;
    var calendar = new FullCalendar.Calendar(el, {
        schedulerLicenseKey: 'AGPL-My-Frontend-And-Backend-Are-Open-Source',
        themeSystem: 'bootstrap5',
        locale: document.documentElement.lang,
        events: location.search ? (location.search + '&events') : '?events',
        eventSourceSuccess: function(raw) {
            return raw.events;
        },
        eventColor: 'var(--bs-primary)',
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
                slotDuration: '00:15:00',
                slotLabelInterval: '01:00:00',
                scrollTime: '08:00:00',
            },
        },
        eventDidMount: function(arg) {
            arg.el.title = arg.event.title;

            if (arg.event.extendedProps.min_subject_count) {
                var container = arg.el.querySelector('.fc-event-title');
                var span = document.createElement('span');
                var iconLabel = $$.gettext('participants');
                span.append('(', $$.icon('fa-solid fa-users', iconLabel), ' ', arg.event.extendedProps.min_subject_count, ')');
                container.append(' ', span);
            }
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
