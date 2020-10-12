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
                td.textContent = date;
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
                td.textContent = time;
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
