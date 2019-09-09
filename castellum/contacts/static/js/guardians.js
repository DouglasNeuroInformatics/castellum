$(function() {
    $(document).on('change', '[name="guardians_pane"]', function() {
        ['self', 'guardians'].forEach(function(id) {
            var $pane = $('#contact-' + id);
            var $radio = $('[name="guardians_pane"][value="' + id + '"]');
            $pane.prop('hidden', !$radio.prop('checked'));
        });
    });
});
