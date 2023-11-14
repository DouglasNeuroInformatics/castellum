var logoutTimeout = parseInt(document.body.getAttribute('data-logout-timeout'), 10) * 1000;
var warnTimeout = logoutTimeout * 0.8;
var pollTimeout = warnTimeout / 10;

var lastActivity = new Date();

var setActive = function() {
    lastActivity = new Date();
};

setInterval(function() {
    var idleTime = new Date() - lastActivity;
    if (idleTime <= pollTimeout) {
        fetch('/ping/', {
            credentials: 'same-origin',
        });
    } else if (idleTime > warnTimeout) {
        // blocks until the alert is closed
        alert(document.querySelector('#i18n-autologout').content.textContent);

        if (new Date() - lastActivity <= logoutTimeout) {
            setActive();
        } else {
            location.reload();
        }
    }
}, pollTimeout);

document.addEventListener('mousemove', setActive);
document.addEventListener('keydown', setActive);
