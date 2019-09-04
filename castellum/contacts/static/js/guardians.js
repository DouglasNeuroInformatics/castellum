$(function() {
    $(document).on('change', '[name="guardians_pane"]', function() {
        ['self', 'guardians'].forEach(function(id) {
            var $pane = $('#contact-' + id);
            var $radio = $('[name="guardians_pane"][value="' + id + '"]');
            $pane.prop('hidden', !$radio.prop('checked'));
        });
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

    $(document).on('click', '[data-js="guardian-remove"]', function() {
        toggleGuardian(this, true);
    });

    $(document).on('click', '[data-js="guardian-restore"]', function() {
        toggleGuardian(this, false);
    });
});
