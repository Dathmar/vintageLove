from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'bespokeShipping'
urlpatterns = [
    path('', views.create, name='create'),
    path('location/<slug:seller_slug>', views.create, name='create-by-seller-id')
]
