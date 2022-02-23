from django.urls import path, include
from . import views


app_name = 'api'
urlpatterns = [
    path('v1/get-delivery-table/', views.get_delivery_table, name='get-delivery-table'),
]
