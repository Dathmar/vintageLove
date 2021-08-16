from django.urls import path
from . import views


app_name = 'store'
urlpatterns = [
    path('', views.index, name='index'),
    path('our-purpose/', views.our_purpose, name='our-purpose'),
    path('join-the-movement/', views.join_movement, name='join_movement'),
]
