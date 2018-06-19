from django.http import HttpResponseRedirect
from django.utils.http import is_safe_url
from django.utils.translation import check_for_language

LANGUAGE_QUERY_PARAMETER = 'language'


def set_language(request):
    """Save language in the user model.

    See also django.views.i18n.set_language
    """
    if request.method == 'POST' and request.user.is_authenticated:
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            request.user.language = lang_code
            request.user.save()

    next = request.POST.get('next', request.GET.get('next'))
    is_safe = is_safe_url(
        next, allowed_hosts=[request.get_host()], require_https=request.is_secure())
    if not is_safe or not next:
        next = '/'

    return HttpResponseRedirect(next)
