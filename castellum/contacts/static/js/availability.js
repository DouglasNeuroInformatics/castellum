(function() {
    var setAll = function(group, value) {
        if (value) {
            group.selected = group.options.map(o => o.value);
        } else {
            group.selected = [];
        }
    };

    Vue.component('availability-group', {
        'props': ['group'],
        'computed': {
            'allDay': {
                'get': function() {
                    return this.group.selected.length === this.group.options.length;
                },
                'set': function(value) {
                    setAll(this.group, value);
                },
            },
            'allDayIndeterminate': function() {
                return this.group.selected.length !== 0;
            },
        },
        'template': `
            <div class="col-6 col-sm-2">
                <div class="form-group">
                    <label for="id_availability_monday">{{ group.label }}</label>
                    <label class="d-block mb-0 mt-n1">
                        <input type="checkbox" v-model="allDay" :indeterminate.prop="allDayIndeterminate">
                        <span class="sr-only">{{ django.gettext('All day') }}</span>
                    </label>
                    <select :name="group.name" class="form-control" :id="group.id" multiple v-model="group.selected">
                        <option v-for="option in group.options" :value="option.value">{{ option.label }}</option>
                    </select>
                </div>
            </div>
        `,
    });

    Vue.component('availability', {
        'props': ['groups'],
        'computed': {
            'allWeek': {
                'get': function() {
                    return this.groups.every(function(group) {
                        return group.selected.length === group.options.length;
                    });
                },
                'set': function(value) {
                    this.groups.forEach(function(group) {
                        setAll(group, value);
                    });
                },
            },
            'allWeekIndeterminate': function() {
                return this.groups.some(function(group) {
                    return group.selected.length !== 0;
                });
            },
        },
        'template': `
            <div class="mb-3">
                <div class="row">
                    <availability-group v-for="group in groups" :group="group"></availability-group>
                </div>
                <label class="form-check mb-0">
                    <input type="checkbox" class="form-check-input" v-model="allWeek" :indeterminate.prop="allWeekIndeterminate">
                    <span class="form-check-label">{{ django.gettext('All week') }}</span>
                </label>
            </div>
        `,
    });

    var getInitialGroups = function($container) {
        var groups = $container.querySelectorAll('.form-group');
        return Array.prototype.map.call(groups, function($group) {
            var $select = $group.querySelector('select');
            return {
                'id': $select.id,
                'name': $select.name,
                'label': $group.querySelector('label').textContent,
                'options': Array.prototype.map.call($select.options, function($option) {
                    return {
                        'value': $option.value,
                        'label': $option.textContent,
                    };
                }),
                'selected': Array.prototype.map.call($select.selectedOptions, function($option) {
                    return $option.value;
                }),
            };
        });
    };

    var containers = document.querySelectorAll('[data-js="availability"]');
    containers.forEach(function($container) {
        new Vue({
            'el': $container,
            'data': {
                'groups': getInitialGroups($container),
            },
            'template': '<availability :groups="groups"></availability>',
        });
    });
})();
