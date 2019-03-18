onReady(function() {
    var oldValue = null;

    var setSensitivity = function() {
        var $studyType = document.querySelector('#id_study_type');
        var $sensitivity = document.querySelector('#id_data_sensitivity');
        var $sensitivityHidden = document.querySelector('#id_data_sensitivity_hidden');

        if ($studyType.value === '2') {
            oldValue = $sensitivity.checked;
            $sensitivity.checked = true;
            $sensitivity.disabled = true;
            $sensitivityHidden.disabled = false;
        } else if ($sensitivity.disabled) {
            $sensitivity.checked = oldValue;
            $sensitivity.disabled = false;
            $sensitivityHidden.disabled = true;
        }
    };

    on(document, 'change', '#id_study_type', setSensitivity);
    setSensitivity();

    var $totalForms = document.querySelector('#id_form-TOTAL_FORMS');
    var $sessionsContainer = document.querySelector('#sessions-container');

    on(document, 'click', '[data-js="session-add"]', function(event) {
        var $template = document.querySelector('#session-data-template');
        var html = $template.innerHTML.replace(/{prefix}/g, 'form-' + $totalForms.value);
        var $wrapper = document.createElement('div');
        $wrapper.innerHTML = html;
        $sessionsContainer.append($wrapper.children[0]);
        $totalForms.value = parseInt($totalForms.value, 10) + 1;
    });

    on(document, 'click', '[data-js="session-delete"]', function(event) {
        var $fieldset = event.target.closest('fieldset');
        var index = Array.prototype.indexOf.call($fieldset.parentElement.children, $fieldset);
        $fieldset.querySelector('[name="form-' + index + '-duration"]').remove();
        $fieldset.innerHTML += '<input type="hidden" name="form-' + index + '-DELETE" value="on">';
        $fieldset.hidden = true;
    });
});
