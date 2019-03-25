$(function() {
    var oldValue = null;

    var setSensitivity = function() {
        var $studyType = $('#id_study_type');
        var $sensitivity = $('#id_data_sensitivity');
        var $sensitivityHidden = $('#id_data_sensitivity_hidden');

        if ($studyType.val() === '2') {
            oldValue = $sensitivity.prop('checked');
            $sensitivity.prop('checked', true);
            $sensitivity.prop('disabled', true);
            $sensitivityHidden.prop('disabled', false);
        } else if ($sensitivity.prop('disabled')) {
            $sensitivity.prop('checked', oldValue);
            $sensitivity.prop('disabled', false);
            $sensitivityHidden.prop('disabled', true);
        }
    };

    $(document).on('change', '#id_study_type', setSensitivity);
    setSensitivity();

    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $sessions_container = $('#sessions-container');

    $(document).on('click', '[data-js="session-add"]', function(event) {
        var $template = $('#session-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $sessions_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="session-delete"]', function(event) {
        var $fieldset = $(event.target).closest('fieldset');
        $fieldset.find('[name="form-' + $fieldset.index() + '-duration"]').remove();
        $fieldset.append($('<input type="hidden" name="form-' + $fieldset.index() + '-DELETE" value="on">'));
        $fieldset.attr('hidden', true);
    });
});
