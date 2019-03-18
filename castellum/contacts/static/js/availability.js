onReady(function() {
    var setCheckbox = function($checkbox, options) {
        if (Array.prototype.every.call(options, o => o.selected)) {
            $checkbox.checked = true;
            $checkbox.indeterminate = false;
        } else if (Array.prototype.every.call(options, o => !o.selected)) {
            $checkbox.checked = false;
            $checkbox.indeterminate = false;
        } else {
            $checkbox.checked = false;
            $checkbox.indeterminate = true;
        }
    };

    var updateCheckboxes = function() {
        var containers = document.querySelectorAll('[data-js="availability"]');
        containers.forEach(function($container) {
            var days = $container.querySelectorAll('.form-group');
            days.forEach(function($day) {
                var $checkbox = $day.querySelector('[data-js="toggle-day"]');
                var options = $day.querySelectorAll('option');
                setCheckbox($checkbox, options);
            });

            var $checkbox = $container.querySelector('[data-js="toggle-all"]');
            var options = $container.querySelectorAll('option');
            setCheckbox($checkbox, options);
        });
    };

    on(document, 'change', '[data-js="availability"] select', updateCheckboxes);

    on(document, 'change', '[data-js="availability"] [type="checkbox"]', function(event) {
        var $container = event.target.closest('.form-group') || event.target.closest('[data-js="availability"]');
        var options = $container.querySelectorAll('option');
        options.forEach(o => o.selected = event.target.checked);
        updateCheckboxes();
    });

    var selects = document.querySelectorAll('[data-js="availability"] select');
    selects.forEach(function($select) {
        var $wrapper = document.createElement('label');
        $wrapper.className = 'd-block mb-0 mt-n1';
        $wrapper.innerHTML += '<input type="checkbox" data-js="toggle-day">';
        $wrapper.innerHTML += '<span class="sr-only">' + django.gettext('All day') + '</span>';
        $select.parentElement.insertBefore($wrapper, $select);
    });

    var containers = document.querySelectorAll('[data-js="availability"]');
    containers.forEach(function($container) {
        var $wrapper = document.createElement('label');
        $wrapper.className = 'form-check mb-0';
        $wrapper.innerHTML += '<input type="checkbox" class="form-check-input" data-js="toggle-all">';
        $wrapper.innerHTML += '<span class="form-check-label">' + django.gettext('All week') + '</span>';
        $container.append($wrapper);
    });

    updateCheckboxes();
});
