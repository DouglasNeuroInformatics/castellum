(function() {
    window.on = function(element, eventType, selector, fn) {
        element.addEventListener(eventType, function(event) {
            var target = event.target.closest(selector);
            if (target && element.contains(target)) {
                fn.call(target, event);
            }
        });
    };

    window.onReady = function(fn) {
        if (document.readyState === 'complete') {
            window.setTimeout(fn);
        } else {
            var handler = function() {
                document.removeEventListener('DOMContentLoaded', handler);
                window.removeEventListener('load', handler);
                fn();
            };

            document.addEventListener('DOMContentLoaded', handler);
            window.addEventListener('load', handler);
        }
    };
})();
