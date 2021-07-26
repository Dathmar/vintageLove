from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'products'
urlpatterns = [
    path('<uuid:product_id>/', views.product, name='product'),
    path('<uuid:product_id>/product_sold', views.product_sold, name='product-sold'),
    path('images/<uuid:product_id>/<int:sequence>/', views.product_image),
    path('qr/<uuid:product_id>/', views.product_qr, name='product-qr'),
    path('', views.product_list, name='all-products'),
]
