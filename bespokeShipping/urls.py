from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'bespokeShipping'
urlpatterns = [
    path('', views.bespoke_shipping_create, name='create'),
]
