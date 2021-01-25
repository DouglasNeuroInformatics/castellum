(function() {
    var totalForms = document.getElementById('id_form-TOTAL_FORMS');
    var container = document.getElementById('filter-forms');

    $$.on(document, 'click', '[data-js="filter-add"]', function() {
        var pk = this.form.description.value;
        var template = document.getElementById('template-' + pk);
        if (template) {
            var formrow = document.createElement('div');
            formrow.className = 'row gx-2 mb-3';
            formrow.innerHTML = template.innerHTML.replace(/{prefix}/g, 'form-' + totalForms.value);
            container.append(formrow);
            totalForms.value = parseInt(totalForms.value, 10) + 1;
            $$.trigger(totalForms, 'change');
        }
    });

    $$.on(document, 'click', '[data-js="filter-delete"]', function() {
        var formrow = this.closest('.row');
        var index = Array.prototype.indexOf.call(formrow.parentElement.children, formrow);

        formrow.querySelector('[name^="form-' + index + '-value"]').remove();

        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'form-' + index + '-DELETE';
        hidden.value = 'on';

        formrow.append(hidden);
        formrow.hidden = true;

        $$.trigger(formrow.querySelector('input'), 'change');
    });
})();
