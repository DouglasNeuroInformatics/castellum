(function() {
    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $sessions_container = $('#sessions-container');

    $(document).on('click', '[data-js="session-add"]', function() {
        var $template = $('#session-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $sessions_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="session-delete"]', function() {
        var $fieldset = $(this).closest('fieldset');
        $fieldset.find('[name="form-' + $fieldset.index() + '-name"]').remove();
        $fieldset.find('[name="form-' + $fieldset.index() + '-duration"]').remove();
        $fieldset.find('[name="form-' + $fieldset.index() + '-resource"]').remove();
        $fieldset.append($('<input type="hidden" name="form-' + $fieldset.index() + '-DELETE" value="on">'));
        $fieldset.attr('hidden', true);
    });
})();
