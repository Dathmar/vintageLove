from django.urls import path, include
from . import views


app_name = 'orders'
urlpatterns = [
    path('create/<uuid:product_id>', views.order_create, name='order_create'),

    # JS fetch urls
    path('square-app-id/', views.square_app_id, name='square-app-id'),
    path('order-nonce/', views.order_nonce, name='order-nonce'),
    path('order-cost/', views.order_cost, name='order-cost'),
]
