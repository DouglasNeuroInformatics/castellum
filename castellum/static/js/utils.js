(function() {
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

    document.querySelectorAll('[type="date"]').forEach(function(e) {
        if (e.type !== 'date') {
            new Datepicker(e, {
                format: 'yyyy-mm-dd',
                language: document.documentElement.lang,
                autoclose: true,
                calendarWeeks: true,
                daysOfWeekHighlighted: [0, 6],
                todayHighlight: true,
            });
        }
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

    $$.on(document, 'click', '[data-animation="success"]', function() {
        this.classList.add('animation-active');
        setTimeout(() => {
            this.classList.remove('animation-active');
        }, 800);
    });

    $.fn.select2.defaults.set('theme', 'bootstrap4');
    $('[data-js="select2"]').select2();
    $('[data-js="select2-tags"]').select2({tags: true});
    $('[data-js="d-select2"] select').select2();
    $('[data-js="d-select2-clear"] select').select2({
        allowClear: true,
        placeholder: '---',
    });
})();
