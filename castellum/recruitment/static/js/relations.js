var select = document.querySelector('#id_other');
var option = select.options[0];
var button = document.querySelector('[data-js="subject-select"]');

button.addEventListener('click', () => {
    $$.popup('/subjects/search-popup/', 'relation-subject-select');
});

select.addEventListener('mousedown', event => {
    if (event.button === 0) {
        event.preventDefault();
        button.focus();
        button.click();
    }
});

window.closeSubjectPopup = function(win, data) {
    if (data) {
        data = JSON.parse(data);
        option.textContent = data.name;
        option.value = data.uuid;
    }
    win.close();
};
