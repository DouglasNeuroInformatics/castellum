$(function() {
    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $appointments_container = $('#appointments-container');

    $(document).on('click', '[data-js="appointment-add"]', function() {
        var $template = $('#appointment-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $appointments_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="appointment-delete"]', function(event) {
        var $fieldset = $(event.target).closest('fieldset');
        $fieldset.find('[name^="form-' + $fieldset.index() + '-start"]').remove();
        $fieldset.append($('<input type="hidden" name="form-' + $fieldset.index() + '-DELETE" value="on">'));
        $fieldset.attr('hidden', true);
    });
});
