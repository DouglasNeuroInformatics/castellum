$(function() {
    $(document).on('change', '[name="has_guardian"]', function() {
        ['self', 'guardians'].forEach(function(id) {
            var $pane = $('#contact-' + id);
            var $radio = $('[name="has_guardian"][value="' + id + '"]');
            $pane.prop('hidden', !$radio.prop('checked'));
        });
    });

    var toggleGuardian = function(el, disabled) {
        var $wrapper = $(el).closest('[data-js="guardian-wrapper"]');
        var $remove = $wrapper.find('[data-js="guardian-remove"]');
        var $restore = $wrapper.find('[data-js="guardian-restore"]');
        var $input = $wrapper.find('input');

        $wrapper.toggleClass('text-muted', disabled);
        $remove.prop('hidden', disabled);
        $restore.prop('hidden', !disabled);
        $input.prop('disabled', disabled);
    };

    $(document).on('click', '[data-js="guardian-remove"]', function() {
        toggleGuardian(this, true);
    });

    $(document).on('click', '[data-js="guardian-restore"]', function() {
        toggleGuardian(this, false);
    });
});
