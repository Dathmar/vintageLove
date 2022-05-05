from django.contrib import admin
from .models import Shipping, ShippingStatus, Quote, ShippingFile, ShippingFileType


# Register your models here.
class ShippingFileInline(admin.TabularInline):
    model = ShippingFile


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('from_name', 'to_name', 'approved', 'paid')


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['id', 'to_name', 'to_email', 'to_phone', 'from_name', 'from_email', 'status', 'create_datetime']
    list_filter = ['status']
    search_fields = ['to_name', 'to_email', 'to_phone', 'from_name', 'from_email']
    list_editable = ['status']

    inlines = [
        ShippingFileInline,
    ]


@admin.register(ShippingStatus)
class ShippingStatusAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(ShippingFileType)
