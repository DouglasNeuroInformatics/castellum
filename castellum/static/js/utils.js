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
            $(e).datepicker({
                format: 'yyyy-mm-dd',
                language: document.documentElement.lang,
                autoclose: true,
                calendarWeeks: true,
                daysOfWeekHighlighted: '0,6',
                todayHighlight: true,
            });
        }
    });

    $$.on(document, 'click', '[data-multi-reset]', function() {
        var targetId = this.dataset.multiReset;
        var target = document.getElementById(targetId);
        target.querySelectorAll('option').forEach(function(element) {
            element.selected = false;
        });
    });

    $$.on(document, 'click', '[data-clipboard]', function() {
        var targetId = this.dataset.clipboard;
        var target = document.getElementById(targetId);
        if (navigator.clipboard) {
            navigator.clipboard.writeText(target.value);
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
})();
