(function() {
    var intl = new Intl.DateTimeFormat(document.documentElement.lang, {weekday: 'long'});
    var DAY_NAMES = [
        intl.format(new Date('2020-01-06')),
        intl.format(new Date('2020-01-07')),
        intl.format(new Date('2020-01-08')),
        intl.format(new Date('2020-01-09')),
        intl.format(new Date('2020-01-10')),
        intl.format(new Date('2020-01-11')),
        intl.format(new Date('2020-01-12')),
    ];

    var $availability = document.querySelector('[data-js="availability"]');
    var $totalForms = document.querySelector('[name="form-TOTAL_FORMS"]');

    var $wrapper = document.createElement('div');
    $wrapper.className = 'mb-3';

    var createId = function() {
        var currentCount = parseInt($totalForms.value, 10);
        $totalForms.value = currentCount + 1;
        return currentCount - 1;
    }

    var createInputCol = function(name, label) {
        var $col = document.createElement('label');
        $col.className = 'col mb-0';

        var $label = document.createElement('span');
        $label.textContent = label;
        $label.className = 'sr-only';
        $col.append($label);

        var $input = document.createElement('input');
        $input.name = name;
        $input.className = 'form-control';
        $col.append($input);

        return $col;
    };

    var deleteRow = function($row, id) {
        var $delInput = document.createElement('input');
        $delInput.type = 'hidden';
        $delInput.name = `form-${id}-DELETE`;
        $delInput.value = 'on';
        $row.append($delInput);

        $row.hidden = true;
    };

    var copyInputProps = function($orig, $input) {
        $input.className = $orig.className;
        $input.value = $orig.value;
        $orig.parentElement.querySelectorAll('.invalid-feedback').forEach($el => {
            $input.parentElement.append($el);
        });
    }

    var addRow = function(day, id) {
        var $day = $wrapper.children[day];
        var $rows = $day.querySelector('[data-js="availability-rows"]');

        var $row = document.createElement('fieldset');
        $row.className = 'form-row mb-1';
        $rows.append($row);

        var $dayInput = document.createElement('input');
        $dayInput.type = 'hidden';
        $dayInput.name = `form-${id}-day`;
        $dayInput.value = day;
        $row.append($dayInput);

        var $pkInput = document.createElement('input');
        $pkInput.type = 'hidden';
        $pkInput.name = `form-${id}-id`;
        $row.append($pkInput);

        $row.append(createInputCol(`form-${id}-start`, django.gettext('Start')));
        $row.append(createInputCol(`form-${id}-end`, django.gettext('End')));

        var $delCol = document.createElement('div');
        $delCol.className = 'col flex-grow-0';
        $row.append($delCol);

        var $del = document.createElement('button');
        $del.type = 'button';
        $del.className = 'btn btn-danger';
        $del.textContent = django.gettext('Delete');
        $del.addEventListener('click', () => deleteRow($row, id));
        $delCol.append($del);

        return $row;
    };

    for (let day = 0; day < 7; day++) {
        let $day = document.createElement('div');
        $day.className = 'row mb-3';
        $wrapper.append($day);

        let $label = document.createElement('strong');
        $label.className = 'col-3 py-1';
        $label.textContent = DAY_NAMES[day];
        $day.append($label);

        let $rows = document.createElement('div');
        $rows.className = 'col';
        $rows.dataset.js = 'availability-rows';
        $day.append($rows);

        let $addCol = document.createElement('div');
        $addCol.className = 'col flex-grow-0';
        $day.append($addCol);

        let $add = document.createElement('button');
        $add.type = 'button';
        $add.className = 'btn btn-link';
        $add.textContent = django.gettext('Add');
        $add.addEventListener('click', () => addRow(day, createId()));
        $addCol.append($add);
    }

    $availability.querySelectorAll('fieldset').forEach($fieldset => {
        $fieldset.remove();

        var $origPk = $fieldset.querySelector('[name$="-id"]');
        var $origDay = $fieldset.querySelector('[name$="-day"]');
        var $origStart = $fieldset.querySelector('[name$="-start"]');
        var $origEnd = $fieldset.querySelector('[name$="-end"]');
        var $origDelete = $fieldset.querySelector('[name$="-DELETE"]');

        if ($origDay.value === '') {
            return;
        }

        var day = parseInt($origDay.value, 10);
        var id = parseInt($origDay.name.slice(5, -4), 10);

        var $row = addRow(day, id);

        var $pkInput = $row.querySelector('[name$="-id"]');
        var $startInput = $row.querySelector('[name$="-start"]');
        var $endInput = $row.querySelector('[name$="-end"]');

        $pkInput.value = $origPk.value;
        copyInputProps($origStart, $startInput);
        copyInputProps($origEnd, $endInput);
        if ($origDelete.checked) {
            deleteRow($row, id);
        }
    });

    $availability.append($wrapper);
})();
