$(function() {
    var mdLight = markdownit({
        breaks: true,
        linkify: true,
    }).disable([
        'heading', 'lheading', 'blockquote', 'fence', 'table',
    ]);

    $('.markdown-light').each(function(i, e) {
        var $e = $(e);
        $e.html(mdLight.render($e.html()));
        $e.css('white-space', 'initial');
    });
});
