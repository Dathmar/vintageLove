from django.contrib import admin
from django.db.models import Q
from .models import Delivery


# Register your models here.
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['user', 'scheduled_date', 'shipping']

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "shipping":
            kwargs["queryset"] = db_field.related_model.objects.filter(status__name="Picked Up")
        return super(DeliveryAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
