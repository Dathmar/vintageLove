from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'orders'
urlpatterns = [
    path('create/<uuid:product_id>', views.order_create, name='order_create'),
    path('bespoke-shipping/', views.bespoke_shipping, name='bespoke-shipping'),
    path('bespoke-shipping/complete', views.bespoke_shipping_complete, name='bespoke-shipping-complete'),

    # JS fetch urls
    path('square-app-id/', views.square_app_id, name='square-app-id'),
    path('order-nonce/', views.order_nonce, name='order-nonce'),
    path('order-cost/', views.order_cost, name='order-cost'),
]
