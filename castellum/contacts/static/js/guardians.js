(function() {
    $$.on(document, 'change', '[name="guardians_pane"]', function() {
        ['self', 'guardians'].forEach(function(id) {
            var $pane = $('#contact-' + id);
            var $radio = $('[name="guardians_pane"][value="' + id + '"]');
            $pane.prop('hidden', !$radio.prop('checked'));
        });
    });

    $$.on(document, 'submit', '[data-js="contact-completeness"]', function(event) {
        var complete = false;
        if ($('[name="guardians_pane"][value="guardians"]').prop('checked')) {
            complete = (
                $('[name="guardians_remove"]:disabled').length ||
                $('[name="guardians_add"]:not(:disabled)').length
            );
        } else {
            complete = (
                $('[name="email"]').val() ||
                $('[name="phone_number"]').val() ||
                $('[name="street"]').val()
            );
        }
        if (!complete) {
            if (!confirm(django.gettext('There is no way to contact this subject. Are you sure you want to save?'))) {
                event.preventDefault();
            }
        }
    });

    var toggleGuardian = function(el, removed) {
        var $wrapper = $(el).closest('[data-js="guardian-wrapper"]');
        var $remove = $wrapper.find('[data-js="guardian-remove"]');
        var $restore = $wrapper.find('[data-js="guardian-restore"]');
        var $input = $wrapper.find('input');

        $wrapper.toggleClass('text-muted', removed);
        $remove.prop('hidden', removed);
        $restore.prop('hidden', !removed);
        if ($input.attr('name') === 'guardians_remove') {
            $input.prop('disabled', !removed);
        } else {
            $input.prop('disabled', removed);
        }
    };

    $$.on(document, 'click', '[data-js="guardian-remove"]', function() {
        toggleGuardian(this, true);
    });

    $$.on(document, 'click', '[data-js="guardian-restore"]', function() {
        toggleGuardian(this, false);
    });

    var addGuardian = function(name, pk) {
        var $template = $('#guardian-template');
        var $button = $('[data-js="guardian-add"]');

        var html = $template.html().replace(/{pk}/g, pk);
        var $el = $(html);
        $el.find('label').text(name);

        $button.before($el);
    };

    $$.on(document, 'click', '[data-js="guardian-add"]', function() {
        // copied from django
        var config = 'height=500,width=800,resizable=yes,scrollbars=yes';
        var win = window.open('/subjects/guardians/', 'guardian-add', config);
        win.focus();
    });

    window.closeGuardianPopup = function(win, data) {
        if (data) {
            data = JSON.parse(data);
            addGuardian(data.name, data.pk);
        }
        win.close();
    };

    $$.on(document, 'click', '[data-js="guardian-dismiss"]', function() {
        window.close();
    });

    var use = function() {
        var data = JSON.stringify($(this).data());
        opener.closeGuardianPopup(window, data);
    };

    $$.on(document, 'click', '[data-js="guardian-use"]', use);
    $('[data-js="guardian-use-auto"]').each(use);
})();
