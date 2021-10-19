from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'folders'
urlpatterns = [
    path('', views.folder_list, name='folder-list'),
    path('folder/not-found/', views.folder_not_found, name='not-found'),
    path('<slug:folder_slug>/', views.folder_view, name='folder-view'),
    path('<slug:folder_slug>/<str:user_name>', views.folder_view, name='folder-view'),

]
