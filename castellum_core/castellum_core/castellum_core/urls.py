from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('admin/', admin.site.urls),
]
