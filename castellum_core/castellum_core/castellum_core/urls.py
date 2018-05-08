from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog


def dummy(request):
    return HttpResponse('', status=204)


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('ping/', dummy, name='ping'),

    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('admin/', admin.site.urls),
]
