var fileInput = document.getElementById('id_file');

var update = function() {
    fileInput.disabled = ['decline', 'delete'].includes(fileInput.form.document.value);
};

fileInput.form.addEventListener('change', update);
update();
