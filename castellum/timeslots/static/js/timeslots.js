(function() {
    var el = document.querySelector('table');

    var getElementIndex = function(el) {
        var i = 0;
        while (el.previousElementSibling) {
            i += 1;
            el = el.previousElementSibling;
        }
        return i;
    };

    var djangoFormatToOptions = function(format) {
        // https://docs.djangoproject.com/en/3.1/ref/templates/builtins/#date
        // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat/DateTimeFormat
        var options = {};
        if (format.includes('d')) {
            options.day = '2-digit';
        } else if (format.includes('j')) {
            options.day = 'numeric';
        }
        if (format.includes('D')) {
            options.weekday = 'short';
        } else if (format.includes('l')) {
            options.weekday = 'long';
        }
        if (format.includes('m')) {
            options.month = '2-digit';
        } else if (format.includes('n')) {
            options.month = 'numeric';
        } else if (format.includes('M') || format.includes('b') || format.includes('N')) {
            options.month = 'short';
        } else if (format.includes('E') || format.includes('F')) {
            options.month = 'long';
        }
        if (format.includes('y')) {
            options.year = '2-digit';
        } else if (format.includes('Y') || format.includes('o')) {
            options.year = 'numeric';
        }
        if (format.includes('g') || format.includes('G')) {
            options.hour = 'numeric';
        } else if (format.includes('h') || format.includes('H')) {
            options.hour = '2-digit';
        }
        if (format.includes('i')) {
            options.minute = '2-digit';
        }
        if (format.includes('s')) {
            options.second = '2-digit';
        }
        if (format.includes('f') || format.includes('P')) {
            options.hour = 'numeric';
            options.minute = 'numeric';
        }
        if (format.includes('e')) {
            options.timeZoneName = 'short';
        }
        if (format.includes('e')) {
            options.timeZoneName = 'short';
        }
        return options;
    };

    var formatDate = function(s, formatName) {
        var format = django.get_format(formatName);
        var options = djangoFormatToOptions(format);
        var lang = document.documentElement.lang;
        var formatter = new Intl.DateTimeFormat(lang, options);
        var date = new Date(s);
        return formatter.format(date);
    };

    var createCell = function(date, time) {
        var td = document.createElement('td');
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'timeslots';
        checkbox.value = date + ' ' + time;
        checkbox.checked = true;
        td.append(checkbox);
        return td;
    };

    var getInsertIndex = function(elements, value, start) {
        var i = start;
        while (i < elements.length && elements[i].dataset.value < value) {
            i += 1;
        }
        return i;
    };

    var addDate = function(table, date) {
        var tbody = table.querySelector('tbody');
        var index = getInsertIndex(tbody.children, date, 0);

        var tr = document.createElement('tr');
        tr.dataset.value = date;

        for (var col of table.querySelectorAll('thead th')) {
            var time = col.dataset.value;
            var td;
            if (!time) {  // first column
                td = document.createElement('th');
                td.textContent = formatDate(date, 'DATE_FORMAT');
            } else {
                td = createCell(date, time);
            }
            tr.append(td);
        }

        if (index < tbody.children.length) {
            tbody.children[index].before(tr);
        } else {
            tbody.append(tr);
        }
    };

    var addTime = function(table, time) {
        var index = getInsertIndex(table.querySelectorAll('thead th'), time, 1);

        for (var tr of table.querySelectorAll('tr')) {
            var date = tr.dataset.value;
            var td;
            if (!date) {  // first row
                td = document.createElement('th');
                td.dataset.value = time;
                td.textContent = formatDate('1970-01-01 ' + time, 'TIME_FORMAT');
            } else {
                td = createCell(date, time);
            }

            if (index < tr.children.length) {
                tr.children[index].before(td);
            } else {
                tr.append(td);
            }
        }
    };

    var rmRow = function(event) {
        event.target.closest('tr').remove();
    };

    var rmCol = function(event) {
        var table = event.target.closest('table');
        var th = event.target.closest('th');
        var i = getElementIndex(th);
        table.querySelectorAll('tr').forEach(tr => {
            tr.children[i].remove();
        });
    };

    $$.on(document, 'submit', '#add_date', function(event) {
        event.preventDefault();
        addDate(el, event.target.input.value);
    });

    $$.on(document, 'submit', '#add_time', function(event) {
        event.preventDefault();
        addTime(el, event.target.input.value);
    });

    $$.on(el, 'click', 'thead th', rmCol);
    $$.on(el, 'click', 'tbody th', rmRow);
})();
