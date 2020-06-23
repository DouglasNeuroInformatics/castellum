(function() {
    var disableInput = function() {
        var $answer_declined = $(this);
        var $target = $('#' + $answer_declined.data('target'));
        $target.prop('disabled', $answer_declined.prop('checked'));
    };

    $$.on(document, 'change', '[data-js="answer-declined"]', disableInput);

    $('[data-js="answer-declined"]').each(function(i, element) {
        disableInput({target: element});
    });
})();
