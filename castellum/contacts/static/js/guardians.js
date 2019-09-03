$(function() {
    $(document).on('change', '[name="has_guardian"]', function() {
        ['self', 'guardians'].forEach(function(id) {
            var $pane = $('#contact-' + id);
            var $radio = $('[name="has_guardian"][value="' + id + '"]');
            $pane.prop('hidden', !$radio.prop('checked'));
        });
    });
});
