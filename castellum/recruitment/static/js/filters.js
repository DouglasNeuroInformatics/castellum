var totalForms = document.getElementById('id_form-TOTAL_FORMS');
var container = document.getElementById('filter-forms');

$$.on(document, 'click', '[data-js="filter-add"]', function() {
    var pk = this.form.attribute.value;
    var template = document.getElementById(`template-${pk}`);
    if (template) {
        var formRow = document.createElement('fieldset');
        formRow.className = 'row gx-2 mb-3';
        formRow.innerHTML = template.innerHTML.replace(/{prefix}/g, `form-${totalForms.value}`);
        container.append(formRow);
        totalForms.value = parseInt(totalForms.value, 10) + 1;
        totalForms.dispatchEvent(new Event('change', {bubbles: true}));
        formRow.querySelector('select').focus();
    }
});

$$.on(document, 'click', '[data-js="filter-delete"]', function() {
    var formRow = this.closest('fieldset');
    var index = Array.prototype.indexOf.call(formRow.parentElement.children, formRow);

    formRow.querySelector(`[name^="form-${index}-value"]`).remove();

    var hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = `form-${index}-DELETE`;
    hidden.value = 'on';

    formRow.append(hidden);
    formRow.hidden = true;

    var input = formRow.querySelector('input');
    input.dispatchEvent(new Event('change', {bubbles: true}));
});
