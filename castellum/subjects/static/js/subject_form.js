$(function() {
    var oldValue = $('#id_no_recruitment').prop('checked');

    var setNoRecruitment = function() {
        var $toBeDeleted = $('#id_to_be_deleted');
        var $noRecruitment = $('#id_no_recruitment');
        var $noRecruitmentHidden = $('#id_no_recruitment_hidden');

        if ($toBeDeleted.prop('checked')) {
            oldValue = $noRecruitment.prop('checked');
            $noRecruitment.prop('checked', true);
            $noRecruitment.prop('disabled', true);
            $noRecruitmentHidden.prop('disabled', false);
        } else {
            $noRecruitment.prop('checked', oldValue);
            $noRecruitment.prop('disabled', false);
            $noRecruitmentHidden.prop('disabled', true);
        }
    };

    $(document).on('change', '#id_to_be_deleted', setNoRecruitment);
    setNoRecruitment();


    var $totalForms = $('#id_form-TOTAL_FORMS');
    var $notes_container = $('#notes-container');

    $(document).on('click', '[data-js="note-add"]', function() {
        var $template = $('#note-data-template');
        var html = $template.html().replace(/{prefix}/g, 'form-' + $totalForms.val());
        var $fieldset = $(html);
        $notes_container.append($fieldset);
        $totalForms.val(parseInt($totalForms.val(), 10) + 1);
    });

    $(document).on('click', '[data-js="note-delete"]', function(event) {
        var $delete = $('#' + event.target.id.slice(0, -6));
        $delete.val(event.target.checked ? '' : 'on');
    });
});
