from django.urls import path
from . import views

app_name = 'seller'
urlpatterns = [

    path('products/', views.product_list, name='product-list'),
    path('products/add/', views.add_product, name='add-product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit-product'),
]
