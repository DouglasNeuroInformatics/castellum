(function() {
    if (navigator.userAgent.indexOf('Trident') !== -1) {
        var el = document.createElement('div');
        el.className = 'bg-warning p-2 text-center';
        el.textContent = 'Internet Explorer is not supported and may not work correctly!';
        document.body.insertBefore(el, document.body.firstChild);
    }
})();
