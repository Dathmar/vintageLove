from django.contrib import admin
from .models import Shipping, ShippingStatus


# Register your models here.
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['to_name', 'to_email', 'from_name', 'from_email']


@admin.register(ShippingStatus)
class ShippingStatusAdmin(admin.ModelAdmin):
    list_display = ['name']
