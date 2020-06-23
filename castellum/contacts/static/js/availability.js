(function() {
    var setCheckbox = function($wrapper, $checkbox) {
        if ($wrapper.find('option:selected').length === 0) {
            $checkbox.prop('checked', false);
            $checkbox.prop('indeterminate', false);
        } else if ($wrapper.find('option:selected').length < $wrapper.find('option').length) {
            $checkbox.prop('checked', false);
            $checkbox.prop('indeterminate', true);
        } else {
            $checkbox.prop('checked', true);
            $checkbox.prop('indeterminate', false);
        }
    };

    var generateCheckboxes = function() {
        // whole week
        var $label = $('<label class="form-check mb-0">');
        $label.append($('<input type="checkbox" class="form-check-input" data-js="toggle-all">'));
        $label.append($('<span class="form-check-label">' + django.gettext('All week') + '</span>'));
        $availability.append($label);

        // whole days
        $availability.find('select').each(function(i, select) {
            var $label = $('<label class="d-block mb-0 mt-n1">');
            $label.append($('<input type="checkbox" data-js="toggle-day">'));
            $label.append($('<span class="sr-only">' + django.gettext('All day') + '</span>'));
            $label.insertBefore(select);
        });
    };

    var $availability = $('[data-js="availability"]');
    generateCheckboxes();
    var $wholeWeek = $('[data-js="toggle-all"]');

    $availability.on('change', 'select', function(event) {
        // hours --> day
        var $wrapperDay = $(event.target);
        var $wholeDay = $(event.target).closest('.form-group').find('[data-js="toggle-day"]');
        setCheckbox($wrapperDay, $wholeDay);

        // hours --> week
        setCheckbox($availability, $wholeWeek);
    });

    $availability.on('change', '[data-js="toggle-day"]', function(event) {
        // day --> hours
        var $wholeDay = $(event.target);
        var $select = $wholeDay.closest('.form-group').find('select');
        $select.find('option').prop('selected', $wholeDay.prop('checked'));

        // day --> week
        setCheckbox($availability, $wholeWeek);
    });

    $availability.on('change', '[data-js="toggle-all"]', function() {
        // week --> hours
        var $wholeWeek = $(event.target);
        $availability.find('option').prop('selected', $wholeWeek.prop('checked'));

        // week --> days
        var $wholeDay = $availability.find('[data-js="toggle-day"]');
        $wholeDay.prop('checked', $wholeWeek.prop('checked'));
        $wholeDay.prop('indeterminate', false);
    });

    // set initial state of day checkboxes
    $('[data-js="toggle-day"]').each(function(i, wholeDay) {
        var $wholeDay = $(wholeDay);
        var $select = $wholeDay.closest('.form-group').find('select');
        setCheckbox($select, $wholeDay);
    });

    // set initial state of week checkbox
    setCheckbox($availability, $wholeWeek);
})();
