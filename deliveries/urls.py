from django.urls import path, include
from . import views


app_name = 'deliveries'
urlpatterns = [
    path('', views.my_assignments, name='my-assignments'),
    path('assignments/create', views.CreateAssignmentsView.as_view(), name='assignments-create'),
]
