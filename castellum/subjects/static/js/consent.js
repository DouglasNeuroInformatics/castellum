var form = document.getElementById('id_file').form;

var update = function() {
    form.file.disabled = !form.document.value;
    form.to_be_deleted.disabled = form.document.value;
};

form.addEventListener('change', update);
update();
