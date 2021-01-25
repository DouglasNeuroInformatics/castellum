(function() {
    var setCheckbox = function(wrapper, checkbox) {
        var options = wrapper.querySelectorAll('option');
        if (Array.prototype.every.call(options, o => !o.selected)) {
            checkbox.checked = false;
            checkbox.indeterminate = false;
        } else if (!Array.prototype.every.call(options, o => o.selected)) {
            checkbox.checked = false;
            checkbox.indeterminate = true;
        } else {
            checkbox.checked = true;
            checkbox.indeterminate = false;
        }
    };

    var generateCheckboxes = function() {
        availability.querySelectorAll('label').forEach(function(label) {
            label.classList.add('mb-0');
        });

        // whole week
        var label = document.createElement('label');
        label.className = 'form-check mb-0';
        label.innerHTML = '<input type="checkbox" class="form-check-input" data-js="toggle-all">' +
            '<span class="form-check-label"></span>';
        label.querySelector('span').textContent = django.gettext('All week');
        availability.append(label);

        // whole days
        availability.querySelectorAll('select').forEach(function(select) {
            var label = document.createElement('label');
            label.className = 'd-block mb-0';
            label.innerHTML = '<input type="checkbox" class="form-check-input" data-js="toggle-day">' +
                '<span class="sr-only"></span>';
            label.querySelector('span').textContent = django.gettext('All day');
            select.before(label);
        });
    };

    var availability = document.querySelector('[data-js="availability"]');
    generateCheckboxes();
    var wholeWeek = document.querySelector('[data-js="toggle-all"]');

    $$.on(availability, 'change', 'select', function() {
        // hours --> day
        var wholeDay = this.closest('.col-6').querySelector('[data-js="toggle-day"]');
        setCheckbox(this, wholeDay);

        // hours --> week
        setCheckbox(availability, wholeWeek);
    });

    $$.on(availability, 'change', '[data-js="toggle-day"]', function() {
        // day --> hours
        var select = this.closest('.col-6').querySelector('select');
        select.querySelectorAll('option').forEach(option => {
            option.selected = this.checked;
        });

        // day --> week
        setCheckbox(availability, wholeWeek);
    });

    $$.on(availability, 'change', '[data-js="toggle-all"]', function() {
        // week --> hours
        availability.querySelectorAll('option').forEach(option => {
            option.selected = this.checked;
        });

        // week --> days
        availability.querySelectorAll('[data-js="toggle-day"]').forEach(wholeDay => {
            wholeDay.checked = this.checked;
            wholeDay.indeterminate = false;
        });
    });

    // set initial state of day checkboxes
    document.querySelectorAll('[data-js="toggle-day"]').forEach(function(wholeDay) {
        var select = wholeDay.closest('.col-6').querySelector('select');
        setCheckbox(select, wholeDay);
    });

    // set initial state of week checkbox
    setCheckbox(availability, wholeWeek);
})();
