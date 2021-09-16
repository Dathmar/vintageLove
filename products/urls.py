from django.urls import path, include
from django.conf.urls import url
from . import views


app_name = 'products'
urlpatterns = [
    path('<uuid:product_id>/', views.product, name='product'),
    path('<slug:product_slug>/', views.product_slug, name='product-slug'),
    path('<uuid:product_id>/product_sold', views.product_sold, name='product-sold'),
    path('images/<uuid:product_id>/<int:sequence>/', views.product_image),
    path('qr/', views.product_qr_list, name='product-qr-list'),
    path('qr/<uuid:product_id>/', views.product_qr, name='product-qr'),
    path('<slug:category_slug>/', views.product_list, name='all-products'),
    path('', views.product_list, name='all-products'),
]
