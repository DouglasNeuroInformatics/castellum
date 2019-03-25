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
        'render': function(h) {
            return h('div', {'class': 'col-6 col-sm-2'}, [
                h('div', {'class': 'form-group'}, [
                    h('label', {'attrs': {'for': 'id_availability_monday'}}, this.group.label),
                    h('label', {'class': 'd-block mb-0 mt-n1'}, [
                        h('input', {
                            'attrs': {
                                'type': 'checkbox',
                            },
                            'domProps': {
                                'checked': this.group.selected.length === this.group.options.length,
                                'indeterminate': this.group.selected.length !== 0,
                            },
                            'on': {
                                'change': event => {
                                    setAll(this.group, event.target.checked);
                                },
                            },
                        }),
                        h('span', {'class': 'sr-only'}, django.gettext('All day')),
                    ]),
                    h('select', {
                        'class': 'form-control',
                        'attrs': {
                            'multiple': '',
                        },
                        'domProps': {
                            'name': this.group.name,
                            'id': this.group.id,
                        },
                        'on': {
                            'change': event => {
                                this.group.selected = Array.prototype.filter.call(event.target.options, o => o.selected).map(o => o.value);
                            },
                        },
                    }, this.group.options.map(option => {
                        return h('option', {
                            'key': option.value,
                            'domProps': {
                                'value': option.value,
                                'selected': this.group.selected.includes(option.value),
                            }
                        }, option.label);
                    })),
                ]),
            ]);
        },
    });

    Vue.component('availability', {
        'props': ['groups'],
        'render': function(h) {
            return h('div', {'class': 'mb-3'}, [
                h('div', {'class': 'row'}, this.groups.map(function(group) {
                    return h('availability-group', {'key': group.id, 'props': {'group': group}});
                })),
                h('label', {'class': 'form-check mb-0'}, [
                    h('input', {
                        'class': 'form-check-input',
                        'attrs': {
                            'type': 'checkbox',
                        },
                        'domProps': {
                            'checked': this.groups.every(function(group) {
                                return group.selected.length === group.options.length;
                            }),
                            'indeterminate': this.groups.some(function(group) {
                                return group.selected.length !== 0;
                            }),
                        },
                        'on': {
                            'change': event => {
                                this.groups.forEach(function(group) {
                                    setAll(group, event.target.checked);
                                });
                            },
                        },
                    }),
                    h('span', {'class': 'form-check-label'}, django.gettext('All week')),
                ]),
            ]);
        },
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
            'render': function(h) {
                return h('availability', {'props': {'groups': this.groups}});
            },
        });
    });
})();
