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
        $(this.form).find('[type="submit"],button:not([type])').prop('disabled', !this.checked);
    });

    $('[type="date"]').each(function(i, e) {
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
        var $target = $($(this).data('multi-reset'));
        $target.find('option').each(function(i, element) {
            $(element).prop('selected', false);
        });
    });

    $$.on(document, 'click', '[data-clipboard]', function() {
        var $target = $($(this).data('clipboard'));
        if (navigator.clipboard) {
            navigator.clipboard.writeText($target.val());
        } else {
            $target.focus();
            $target[0].setSelectionRange(0, 1000);
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
