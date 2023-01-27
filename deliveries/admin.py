from django.contrib import admin
from django.db.models import Q
from .models import Delivery, EquipmentStatus, PdService


# Register your models here.
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'scheduled_date', 'shipping', 'sequence', 'blocked', 'pickup', 'complete']
    list_filter = ['user', 'scheduled_date', 'blocked', 'pickup', 'complete']
    search_fields = ['id__exact', 'shipping__exact']


@admin.register(EquipmentStatus)
class EquipmentStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'timeperiod', 'mileage', 'fuel_level']


admin.site.register(PdService)
