from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'bespokeShipping'
urlpatterns = [
    path('', views.my_deliveries, name='my-deliveries'),
    # path('ship-create-view/', views.CreateView.as_view(), name='ship-create-view'),
]
