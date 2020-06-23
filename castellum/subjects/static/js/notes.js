(function() {
    var totalForms = document.getElementById('id_form-TOTAL_FORMS');
    var notesContainer = document.getElementById('notes-container');

    $$.on(document, 'click', '[data-js="note-add"]', function() {
        var template = document.getElementById('note-data-template');
        var wrapper = document.createElement('div');
        wrapper.innerHTML = template.innerHTML.replace(/{prefix}/g, 'form-' + totalForms.value);
        notesContainer.append(wrapper.children[0]);
        totalForms.value = parseInt(totalForms.value, 10) + 1;
        $$.trigger(totalForms, 'change');
    });

    $$.on(document, 'click', '[data-js="note-delete"]', function() {
        var target = document.getElementById(this.id.slice(0, -6));
        target.value = this.checked ? '' : 'on';
    });
})();
