(function() {
    var input = document.querySelector('[name="street"]');
    var list = document.createElement('datalist');
    list.id = input.id + '_list';
    input.after(list);
    input.setAttribute('list', list.id);

    $$.on(document, 'input', '[name="street"]', function() {
        fetch('/contacts/streets/?q=' + this.value, {credentials: 'same-origin'})
            .then(response => response.json())
            .then(json => {
                list.innerHTML = '';
                for (var name of json.streets) {
                    var option = document.createElement('option');
                    option.textContent = name;
                    list.append(option);
                }
            });
    });
})();
