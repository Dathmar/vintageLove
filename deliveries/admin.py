from django.contrib import admin
from django.db.models import Q
from .models import Delivery


# Register your models here.
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['user', 'scheduled_date', 'shipping', 'sequence', 'blocked', 'pickup', 'complete']


