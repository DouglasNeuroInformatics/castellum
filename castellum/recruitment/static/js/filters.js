var totalForms = document.getElementById('id_form-TOTAL_FORMS');
var container = document.getElementById('filter-forms');
var btn = document.querySelector('[data-js="filter-add"]');

function getFormPrefix(formRow) {
    var field = formRow.querySelector('[name^="form-"]');
    return field.name.match(/^form-\d+/)[0];
}

function deleteFilterForm(formRow) {
    var prefix = getFormPrefix(formRow);
    formRow.querySelector(`[name^="${prefix}-value"]`)?.remove();
    
    var hidden = formRow.querySelector(`[name="${prefix}-DELETE"]`);
    if (!hidden) {
        hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = `${prefix}-DELETE`;
        formRow.append(hidden);
    }

    hidden.type = 'hidden';
    hidden.value = 'on';
    hidden.dispatchEvent(new Event('change', {bubbles: true}));

    formRow.hidden = true;
}

btn.addEventListener('click', function () {
    var pk = this.form.attribute.value;
    var template = document.getElementById(`template-${pk}`);
    var prefix = `form-${totalForms.value}`;
    if (template) {
        var formRow = document.createElement('fieldset');
        formRow.className = 'row gx-2 mb-3';
        formRow.innerHTML = template.innerHTML.replace(/{prefix}/g, prefix);

        var deleteColumn = document.createElement('div');
        deleteColumn.className = 'col-sm flex-grow-0';

        var deleteButton = document.createElement('button');
        deleteButton.type = 'button';
        deleteButton.className = 'btn btn-danger';
        deleteButton.textContent = $$.gettext('delete');
        deleteButton.setAttribute('data-js', 'filter-delete');

        deleteColumn.appendChild(deleteButton);
        formRow.appendChild(deleteColumn);
        container.append(formRow);

        totalForms.value = parseInt(totalForms.value, 10) + 1;
        totalForms.dispatchEvent(new Event('change', {bubbles: true}));
        formRow.querySelector('select').focus();
    }
});

$$.on(document, 'click', '[data-js="filter-delete"]', function() {
    var formRow = this.closest('fieldset');
    deleteFilterForm(formRow);
});
