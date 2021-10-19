from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'folders'
urlpatterns = [
    path('', views.folder_list, name='folder-list'),
    path('<slug:folder_slug>/', views.folder_view, name='folder-view'),
]
