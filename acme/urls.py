from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'acme'
urlpatterns = [
    path('<str:acme_url>', views.challenge),
]
