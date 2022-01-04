from django.contrib import admin
from .models import Shipping, ShippingStatus, Quote


# Register your models here.
@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['to_name', 'to_email', 'to_phone', 'from_name', 'from_email', 'status', 'order_window']
    list_filter = ['status', 'order_window']
    search_fields = ['to_name', 'to_email', 'to_phone', 'from_name', 'from_email']
    list_editable = ['status', 'order_window']


@admin.register(ShippingStatus)
class ShippingStatusAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(Quote)
