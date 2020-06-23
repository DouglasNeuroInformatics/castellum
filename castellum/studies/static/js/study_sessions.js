(function() {
    var totalForms = document.getElementById('id_form-TOTAL_FORMS');
    var sessionsContainer = document.getElementById('sessions-container');

    $$.on(document, 'click', '[data-js="session-add"]', function() {
        var template = document.getElementById('session-data-template');
        var wrapper = document.createElement('div');
        wrapper.innerHTML = template.innerHTML.replace(/{prefix}/g, 'form-' + totalForms.value);
        sessionsContainer.append(wrapper.children[0]);
        totalForms.value = parseInt(totalForms.value, 10) + 1;
    });

    $$.on(document, 'click', '[data-js="session-delete"]', function() {
        var fieldset = this.closest('fieldset');
        var index = Array.prototype.indexOf.call(fieldset.parentElement.children, fieldset);

        fieldset.querySelector('[name="form-' + index + '-name"]').remove();
        fieldset.querySelector('[name="form-' + index + '-duration"]').remove();
        fieldset.querySelector('[name="form-' + index + '-resource"]').remove();

        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = 'form-' + index + '-DELETE';
        hidden.value = 'on';
        fieldset.appendChild(hidden);

        fieldset.hidden = true;
    });
})();
