from django.urls import path, include
from . import views


app_name = 'bespokeShipping'
urlpatterns = [
    path('', views.create, name='create'),
    path('location/<slug:seller_slug>/', views.create, name='create-by-seller-id'),
    path('ship-cost/', views.ship_cost, name='ship-cost'),
    path('qr-grid/', views.qr_grid, name='qr-grid'),
    path('ship-create-view/', views.CreateView.as_view(), name='ship-create-view'),
    path('quote/', views.quote_context, name='quote-context'),
    path('quote/<slug:seller_slug>/', views.CreateQuoteView.as_view(), name='quote-create'),
]
