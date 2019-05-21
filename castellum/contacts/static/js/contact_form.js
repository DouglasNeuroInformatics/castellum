$(function() {
    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $notes_container = $('#notes-container');

    $(document).on('click', '[data-js="note-add"]', function(event) {
        var $template = $('#note-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $notes_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="note-delete"]', function(event) {
        var $fieldset = $(event.target).closest('fieldset');
        $fieldset.find('[name="form-' + $fieldset.index() + '-content"]').remove();
        $fieldset.append($('<input type="hidden" name="form-' + $fieldset.index() + '-DELETE" value="on">'));
        $fieldset.attr('hidden', true);
    });
});
