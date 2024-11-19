var fileInput = document.getElementById('id_file');

var update = function() {
    fileInput.disabled = !/\d+/.test(fileInput.form.document.value);
};

fileInput.form.addEventListener('change', update);
update();
