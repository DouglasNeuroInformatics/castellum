var select = function() {
    var data = JSON.stringify(this.dataset);
    opener.closeSubjectPopup(window, data);
};

$$.on(document, 'click', '[data-js="popup-dismiss"]', () => window.close());
$$.on(document, 'click', '[data-js="popup-select"]', select);
document.querySelectorAll('[data-js="popup-select-auto"]').forEach(el => select.call(el));
