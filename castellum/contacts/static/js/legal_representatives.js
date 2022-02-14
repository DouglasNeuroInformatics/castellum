(function() {
    $$.on(document, 'change', '[name="pane"]', function() {
        ['self', 'legal_representatives'].forEach(function(id) {
            var pane = document.getElementById('contact-' + id);
            var radio = document.querySelector('[name="pane"][value="' + id + '"]');
            pane.hidden = !radio.checked;
        });
    });

    $$.on(document, 'submit', '[data-js="contact-completeness"]', function(event) {
        var complete = false;
        if (document.querySelector('[name="pane"][value="legal_representatives"]').checked) {
            complete = (
                document.querySelector('[name="legal_representatives_remove"]:disabled') ||
                document.querySelector('[name="legal_representatives_add"]:not(:disabled)') ||
                document.querySelector('[data-js="legal-representatives-blocked"]')
            );
        } else {
            complete = (
                document.querySelector('[name="email"]').value ||
                document.querySelector('[name="phone_number"]').value ||
                document.querySelector('[name="street"]').value
            );
        }
        if (!complete) {
            if (!confirm(django.gettext('There is no way to contact this subject. Are you sure you want to save?'))) {
                event.preventDefault();
            }
        }
    });

    var toggleLegalRepresentative = function(el, removed) {
        var wrapper = el.closest('[data-js="legal-representative-wrapper"]');
        var remove = wrapper.querySelector('[data-js="legal-representative-remove"]');
        var restore = wrapper.querySelector('[data-js="legal-representative-restore"]');
        var input = wrapper.querySelector('input');

        wrapper.classList.toggle('text-muted', removed);
        remove.hidden = removed;
        restore.hidden = !removed;
        if (input.name === 'legal_representatives_remove') {
            input.disabled = !removed;
        } else {
            input.disabled = removed;
        }
    };

    $$.on(document, 'click', '[data-js="legal-representative-remove"]', function() {
        toggleLegalRepresentative(this, true);
    });

    $$.on(document, 'click', '[data-js="legal-representative-restore"]', function() {
        toggleLegalRepresentative(this, false);
    });

    var addLegalRepresentative = function(name, uuid) {
        var template = document.getElementById('legal-representative-template');
        var button = document.querySelector('[data-js="legal-representative-add"]');

        var wrapper = document.createElement('div');
        wrapper.innerHTML = template.innerHTML.replace(/{uuid}/g, uuid);
        wrapper.querySelector('label').textContent = name;

        button.before(wrapper.children[0]);
        jdenticon();
    };

    $$.on(document, 'click', '[data-js="legal-representative-add"]', function() {
        // copied from django
        var config = 'height=500,width=800,resizable=yes,scrollbars=yes';
        var win = window.open('/subjects/representatives/', 'legal-representative-add', config);
        win.focus();
    });

    window.closeLegalRepresentativePopup = function(win, data) {
        if (data) {
            data = JSON.parse(data);
            addLegalRepresentative(data.name, data.uuid);
        }
        win.close();
    };

    $$.on(document, 'click', '[data-js="legal-representative-dismiss"]', function() {
        window.close();
    });

    var use = function() {
        var data = JSON.stringify(this.dataset);
        opener.closeLegalRepresentativePopup(window, data);
    };

    $$.on(document, 'click', '[data-js="legal-representative-use"]', use);
    document.querySelectorAll('[data-js="legal-representative-use-auto"]').forEach(el => use.call(el));
})();
