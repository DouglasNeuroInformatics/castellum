$(function() {
    var submitted = false;

    var registerBeforeUnload = function() {
        $(window).on('beforeunload', function(event) {
            if (!submitted) {
                event.preventDefault();
                // Chrome requires returnValue to be set.
                event.returnValue = '';
            }
        });
    };

    $('[data-js="unsaved-changes"]')
    .on('change', registerBeforeUnload)
    .on('submit', function(event) {
        submitted = true;
    });

    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $container = $('#filter-forms');

    $(document).on('click', '[data-js="filter-add"]', function(event) {
        var pk = event.target.form.description.value;
        var $template = $('#template-' + pk);
        if ($template.length) {
            var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
            var $fieldset = $('<div class="form-row mb-3">').html(html);
            $container.append($fieldset);
            $totalForms.val(parseInt($totalForms.val(), 10) + 1);
            registerBeforeUnload();
        }
    });

    $(document).on('click', '[data-js="filter-delete"]', function(event) {
        var $fieldset = $(event.target).closest('.form-row');
        $fieldset.find('[name^="form-' + $fieldset.index() + '-value"]').remove();
        $fieldset.append($('<input type="hidden" name="form-' + $fieldset.index() + '-DELETE" value="on">'));
        $fieldset.attr('hidden', true);
        registerBeforeUnload();
    });
});
