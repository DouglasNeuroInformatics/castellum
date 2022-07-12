(function() {
    var fileInput = document.getElementById('id_file');

    var update = function() {
        fileInput.disabled = !fileInput.form.document.value;
    };

    fileInput.form.addEventListener('change', update);
    update();
})();
