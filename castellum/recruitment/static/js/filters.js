(function() {
    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $container = $('#filter-forms');

    $$.on(document, 'click', '[data-js="filter-add"]', function() {
        var pk = this.form.description.value;
        var $template = $('#template-' + pk);
        if ($template.length) {
            var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
            var $formrow = $('<div class="form-row mb-3">').html(html);
            $container.append($formrow);
            $totalForms.val(parseInt($totalForms.val(), 10) + 1).trigger('change');
        }
    });

    $$.on(document, 'click', '[data-js="filter-delete"]', function() {
        var $formrow = $(this).closest('.form-row');
        $formrow.find('[name^="form-' + $formrow.index() + '-value"]').remove();
        $formrow.append($('<input type="hidden" name="form-' + $formrow.index() + '-DELETE" value="on">'));
        $formrow.attr('hidden', true);
        $formrow.find('input').trigger('change');
    });
})();
