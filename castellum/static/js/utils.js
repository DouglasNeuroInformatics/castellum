window.$$ = {
    on: function(el, eventName, selector, fn) {
        el.addEventListener(eventName, function(event) {
            var target = event.target.closest(selector);
            if (target) {
                fn.call(target, event);
            }
        });
    },
    trigger: function(el, eventName) {
        var event = document.createEvent('HTMLEvents');
        event.initEvent(eventName, true, false);
        el.dispatchEvent(event);
    },
    throttled: function(fn, timeout) {
        var blocked = false;
        return function() {
            if (!blocked) {
                blocked = true;
                setTimeout(() => {
                    fn.apply(this, arguments);
                    blocked = false;
                }, timeout);
            }
        };
    },
    icon: function(cls, label) {
        var i = document.createElement('i');
        i.className = cls;
        if (label) {
            i.title = label;
            i.setAttribute('aria-label', label);
        }
        return i;
    },
    gettext: function(key) {
        return document.querySelector(`#i18n-${key}`).content.textContent;
    },
};

var preventDoubleClick = false;
$$.on(document, 'submit', 'form', function(event) {
    if (preventDoubleClick) {
        event.preventDefault();
    } else {
        preventDoubleClick = true;
        setTimeout(function() {
            preventDoubleClick = false;
        }, 1000);
    }
});

$$.on(document, 'change', '[data-js="confirm-delete"]', function() {
    this.form.querySelector('[type="submit"],button:not([type])').disabled = !this.checked;
});

$$.on(document, 'click', '[data-clipboard]', function() {
    var targetSelector = this.dataset.clipboard;
    var target = document.querySelector(targetSelector);
    if (navigator.clipboard) {
        navigator.clipboard.writeText(target.value || target.href);
    } else {
        target.focus();
        target.setSelectionRange(0, 1000);
        document.execCommand('copy');
    }
});

$$.on(document, 'click', '[data-js="popup"]', function(event) {
    event.preventDefault();
    // copied from django
    var config = 'height=500,width=800,resizable=yes,scrollbars=yes';
    var win = window.open(this.href, null, config);
    win.focus();
});

$$.on(document, 'click', '[data-js="clear-datetime"]', function() {
    this.closest('.row').querySelectorAll('input').forEach(el => {
        el.value = '';
        $$.trigger(el, 'change');
    });
});

$$.on(document, 'click', '[data-animation="success"]', function() {
    this.classList.add('animation-active');
    setTimeout(() => {
        this.classList.remove('animation-active');
    }, 800);
});

$$.on(document, 'click', '[data-js="replace-me"]', function(event) {
    event.preventDefault();

    if (this.querySelector('.fa-spinner')) {
        return;
    }

    var spinner = document.createElement('i');
    spinner.className = 'fa fa-spinner fa-pulse';
    this.append(spinner);

    fetch(this.href, {credentials: 'same-origin'})
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                throw response;
            }
        })
        .then(pseudonym => this.parentElement.textContent = pseudonym)
        .catch(() => spinner.remove());
});

$$.on(document, 'click', '[data-js="submit"]', function() {
    fetch(this.dataset.action, {
        credentials: 'same-origin',
        method: 'POST',
        body: new FormData(this.form),
    });
});

$.fn.select2.defaults.set('theme', 'bootstrap4');
$('[data-js="select2"]').select2();
$('[data-js="select2-tags"]').select2({tags: true});
$('[data-js="d-select2"] select').select2();
$('[data-js="d-select2-clear"] select').select2({
    allowClear: true,
    placeholder: '---',
});

var prefixColor = function(state) {
    if (!state.element) {
        return null;
    }
    var $badge = $('<span class="w-100 badge">&nbsp</span>');
    $badge.addClass(`text-bg-${state.element.value}`);
    $badge.attr('aria-label', state.text);
    return $badge;
};

$('[data-js="d-select2-color"] select').select2({
    minimumResultsForSearch: -1,
    templateResult: prefixColor,
    templateSelection: prefixColor,
});

var firstErrorInTab = document.querySelector(
    '[role="tabpanel"] form .alert-danger, [role="tabpanel"] .is-invalid'
);
if (firstErrorInTab) {
    var panel = firstErrorInTab.closest('[role="tabpanel"]');
    var tab = document.getElementById(panel.getAttribute('aria-labelledby'));
    new bootstrap.Tab(tab).show();
}

var ageDifference = function(a, b) {
    if (isNaN(a) || isNaN(b) || b < a) {
        return '—';
    }

    var years = b.getFullYear() - a.getFullYear();
    var months = b.getMonth() - a.getMonth();
    var days = b.getDate() - a.getDate();
    var totalMonths = years * 12 + months + (days < 0 ? -1 : 0);

    if (totalMonths >= 12 * 6) {
        return $$.gettext('years').replace('%i', Math.floor(totalMonths / 12));
    } else if (totalMonths >= 12 * 2) {
        return [
            $$.gettext('years').replace('%i', Math.floor(totalMonths / 12)),
            $$.gettext('months').replace('%i', totalMonths % 12),
        ].join(', ');
    }

    var tmp = new Date(a.getFullYear(), a.getMonth() + totalMonths, a.getDate());
    // clip to last day of month
    if (tmp.getMonth() !== (a.getMonth() + totalMonths) % 24) {
        tmp.setDate(0);
    }
    return [
        $$.gettext('months').replace('%i', totalMonths),
        $$.gettext('days').replace('%i', Math.round((b - tmp) / 24 / 3600 / 1000)),
    ].join(', ');
};

var updateAge = function(el) {
    var [a, b] = el.dataset.age.split(' ', 2).map(s => {
        if (s.startsWith('#')) {
            return new Date(document.querySelector(s).value);
        } else {
            return new Date(s);
        }
    });
    el.textContent = ageDifference(a, b);
};

document.querySelectorAll('[data-age]').forEach(el => {
    el.dataset.age.split(' ', 2).forEach(s => {
        if (s.startsWith('#')) {
            var target = document.querySelector(s);
            target.addEventListener('change', () => updateAge(el));
        }
    });
    updateAge(el);
});
