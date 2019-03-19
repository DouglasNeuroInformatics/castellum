$(function() {
    //checkbox-setter
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

    $(document).on('change', '[data-js="availability"] select', function(event) {
        // hours --> day
        var $wrapperDay = $(event.target);
        var $checkboxDay = $(event.target).closest('.form-group').find('[data-js="toggle-day"]');
        setCheckbox($wrapperDay, $checkboxDay);
        
        // hours --> week
        var $wrapperWeek = $(event.target).closest('[data-js="availability"]');
        var $checkboxWeek = $('[data-js="toggle-all"]');
        setCheckbox($wrapperWeek, $checkboxWeek);
    });

    $(document).on('change', '[data-js="availability"] [data-js="toggle-day"]', function(event) {
        // day --> hours
        var $wholeDay = $(event.target);
        var $select = $wholeDay.closest('.form-group').find('select');
        $select.find('option').prop('selected', $wholeDay.prop('checked'));
        
        // day --> week
        var $wrapper = $(event.target).closest('[data-js="availability"]');
        var $checkbox = $('[data-js="toggle-all"]');
        setCheckbox($wrapper, $checkbox);
    });

    $(document).on('change', '[data-js="toggle-all"]', function() {
        // week --> hours
        var $wholeWeek = $(event.target);
        $wholeWeek.closest('[data-js="availability"]').find('option').prop('selected', $wholeWeek.prop('checked'));

        // week --> days
        var $wholeDay = $wholeWeek.closest('[data-js="availability"]').find('[data-js="toggle-day"]');
        $wholeDay.prop('checked', $wholeWeek.prop('checked'));
        $wholeDay.prop('indeterminate', false);
    });

    // checkboxes for days
    $('[data-js="availability"] select').each(function(i, select) {
        var $wrapper = $('<label class="d-block mb-0 mt-n1">');
        $wrapper.append($('<input type="checkbox" data-js="toggle-day">'));
        $wrapper.append($('<span class="sr-only">' + django.gettext('All day') + '</span>'));
        $wrapper.insertBefore(select);
    });

    // checkboxes for week
    var $wrapper = $('<label class="form-check mb-0">');
    $wrapper.append($('<input type="checkbox" class="form-check-input" data-js="toggle-all">'));
    $wrapper.append($('<span class="form-check-label">' + django.gettext('All week') + '</span>'));
    $('[data-js="availability"]').append($wrapper);

    // set initial state of day checkboxes
    $('[data-js="toggle-day"]').each(function(i, wholeDay) {
        var $wholeDay = $(wholeDay);
        var $select = $wholeDay.closest('.form-group').find('select');
        setCheckbox($select, $wholeDay);
    });
    // set initial state of week checkbox
    var $wholeWeek = $('[data-js="toggle-all"]');
    var $wrapper = $('[data-js="availability"]');
    setCheckbox($wrapper, $wholeWeek);

});