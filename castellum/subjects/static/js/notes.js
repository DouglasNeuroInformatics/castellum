(function() {
    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $notes_container = $('#notes-container');

    $(document).on('click', '[data-js="note-add"]', function() {
        var $template = $('#note-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $notes_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="note-delete"]', function() {
        var $delete = $('#' + this.id.slice(0, -6));
        $delete.val(this.checked ? '' : 'on');
    });
})();
