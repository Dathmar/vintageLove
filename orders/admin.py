from django.contrib import admin
from .models import Order, OrderItem


# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address1', 'address2', 'postal_code', 'city',
                    'state', 'paid', 'create_datetime', 'update_datetime']
    list_filter = ['paid', 'create_datetime', 'update_datetime']
    inlines = [OrderItemInline]
