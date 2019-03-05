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
});
