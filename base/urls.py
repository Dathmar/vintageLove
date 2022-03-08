from django.urls import path
from . import views


app_name = 'base'
urlpatterns = [
    path('urls/', views.url_list, name='url-list'),
]
