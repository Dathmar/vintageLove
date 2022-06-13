from django.urls import path, include
from . import views


app_name = 'api'
urlpatterns = [
    path('v1/get-delivery-table/', views.get_delivery_table, name='get-delivery-table'),
    path('v1/create-assignment/', views.create_assignment, name='create-assignment'),
    path('v1/update-assignment/<int:delivery_id>/', views.update_assignment, name='update-assignment'),
    path('v1/approve-quote/<uuid:quote_id>/', views.approve_quote, name='approve-quote'),
]
