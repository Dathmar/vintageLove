from django.urls import path, include
from . import views


app_name = 'deliveries'
urlpatterns = [
    path('', views.my_deliveries, name='my-deliveries'),
    # path('ship-create-view/', views.CreateView.as_view(), name='ship-create-view'),
]
