from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'bespokeShipping'
urlpatterns = [
    path('', views.create, name='create'),
    path('location/<slug:seller_slug>/', views.create, name='create-by-seller-id'),
    path('ship-cost/', views.ship_cost, name='ship-cost'),
    path('qr-grid/', views.qr_grid, name='qr-grid'),
]
