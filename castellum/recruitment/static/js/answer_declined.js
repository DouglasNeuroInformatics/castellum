var disableInput = function() {
    var targetId = this.dataset.target;
    var target = document.getElementById(targetId);
    target.disabled = this.checked;
};

$$.on(document, 'change', '[data-js="answer-declined"]', disableInput);

document.querySelectorAll('[data-js="answer-declined"]').forEach(function(element) {
    disableInput.call(element);
});
