from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'folders'
urlpatterns = [
    path('', views.folder_list, name='folder-list'),

]
