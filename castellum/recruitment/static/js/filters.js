onReady(function() {
    var submitted = false;

    var registerBeforeUnload = function() {
        window.addEventListener('beforeunload', function(event) {
            if (!submitted) {
                event.preventDefault();
                // Chrome requires returnValue to be set.
                event.returnValue = '';
            }
        });
    };

    on(document, 'change', '[data-js="unsaved-changes"]', registerBeforeUnload);
    on(document, 'submit', '[data-js="unsaved-changes"]', function(event) {
        submitted = true;
    });

    var $totalForms = document.querySelector('#id_form-TOTAL_FORMS');
    var $container = document.querySelector('#filter-forms');

    on(document, 'click', '[data-js="filter-add"]', function(event) {
        var pk = event.target.form.description.value;
        var $template = document.querySelector('#template-' + pk);
        if ($template) {
            var html = $template.innerHTML.replace(/{prefix}/g, 'form-' + $totalForms.value);
            var $fieldset = document.createElement('fieldset');
            $fieldset.className = 'row mb-3';
            $fieldset.innerHTML = html;
            $container.append($fieldset);
            $totalForms.value = parseInt($totalForms.value, 10) + 1;
            registerBeforeUnload();
        }
    });

    on(document, 'click', '[data-js="filter-delete"]', function(event) {
        var $fieldset = event.target.closest('fieldset');
        var index = Array.prototype.indexOf.call($fieldset.parentElement.children, $fieldset);
        $fieldset.querySelectorAll('[name^="form-' + index + '-value"]').forEach(function($e) {
            $e.remove();
        });
        $fieldset.innerHTML += '<input type="hidden" name="form-' + index + '-DELETE" value="on">';
        $fieldset.hidden = true;

        registerBeforeUnload();
    });
});
