from django.urls import path
from . import views

app_name = 'products'
urlpatterns = [

    path('images/<uuid:product_id>/<int:sequence>/<str:size>', views.product_image, name='product_image'),
    path('qr/', views.product_qr_list, name='product-qr-list'),
    path('qr/<uuid:product_id>/', views.product_qr, name='product-qr'),
    path('categroy/<slug:category_slug>/', views.product_list, name='all-products'),
    path('stage/<slug:stage>/', views.product_list_stage, name='stage-products'),
    path('', views.product_list, name='all-products'),
    path('qr-grid/', views.product_qr_grid, name='qr-grid'),
    path('<uuid:product_id>/', views.product, name='product'),
    path('<uuid:product_id>/product_sold/', views.product_sold, name='product-sold'),
    path('<slug:product_slug>/', views.product_w_slug, name='product-slug'),
    path('seller/<slug:seller_slug>/', views.seller_products, name='seller-products'),
    path('estate/<slug:seller_slug>/', views.seller_products, name='seller-products'),
]
