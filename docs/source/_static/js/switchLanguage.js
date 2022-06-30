function switchLanguage(originLanguage, targetLanguage) {
    var url = window.location.href;
    var target_url = url.replace('/' + originLanguage + '/', '/' + targetLanguage + '/');
    location.assign(target_url);
}