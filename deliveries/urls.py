from django.urls import path, include
from . import views


app_name = 'deliveries'
urlpatterns = [
    path('', views.my_assignments, name='my-assignments'),
    path('block/<int:delivery_id>/', views.block_assignment, name='block-assignment'),
    path('unblock/<int:delivery_id>/', views.unblock_assignment, name='unblock-assignment'),
    path('complete/<int:delivery_id>/', views.complete_assignment, name='complete-assignment'),
    path('assignments/create/', views.CreateAssignmentsView.as_view(), name='assignments-create'),
    path('assignments/associate/', views.AssociateAssignmentsView.as_view(), name='assignments-associate'),
    path('equipment-status/<str:tod>/', views.EquipmentStatusView.as_view(), name='equipment-status'),
]
