from django.urls import path

from .example import MyDynamicUpdateView

app_name = 'dynamic'
urlpatterns = [
    path('<int:pk>/', MyDynamicUpdateView.as_view(), name='update'),
]
