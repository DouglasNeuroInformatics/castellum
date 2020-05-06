$(function() {
    var preventDoubleClick = false;
    $(document).on('submit', 'form', function(event) {
        if (preventDoubleClick) {
            event.preventDefault();
        } else {
            preventDoubleClick = true;
            setTimeout(function() {
                preventDoubleClick = false;
            }, 1000);
        }
    });

    $(document).on('change', '[data-js="confirm-delete"]', function() {
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

    $(document).on('click', '[data-multi-reset]', function(event) {
        var $target = $($(event.target).data('multi-reset'));
        $target.find('option').each(function(i, element) {
            $(element).prop('selected', false);
        });
    });

    $(document).on('click', '[data-clipboard]', function(event) {
        var $target = $($(event.target).data('clipboard'));
        if (navigator.clipboard) {
            navigator.clipboard.writeText($target.val());
        } else {
            $target.focus();
            $target[0].setSelectionRange(0, 1000);
            document.execCommand('copy');
        }
    });

    $(document).on('click', '[data-js="popup"]', function(event) {
        event.preventDefault();
        // copied from django
        var config = 'height=500,width=800,resizable=yes,scrollbars=yes';
        var win = window.open(event.target.href, null, config);
        win.focus();
    });
});
