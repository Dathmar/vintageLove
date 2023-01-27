from django.contrib import admin
from .models import Shipping, ShippingStatus, Quote, ShippingFile, ShippingFileType
import csv
from django.http import HttpResponse
import datetime


@admin.action(description='Export Selected')
def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;' 'filename={}.csv'.format(opts.verbose_name)
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)

    return response


# Register your models here.
class ShippingFileInline(admin.TabularInline):
    model = ShippingFile


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('encoding', 'from_name', 'to_name', 'approved', 'paid')
    search_fields = ['to_name', 'from_name', 'encoding']

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            queryset |= self.model.objects.filter(to_name__icontains=search_term)
        else:
            queryset |= self.model.objects.filter(id__exact=search_term_as_int)
        return queryset, may_have_duplicates


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ['id', 'to_name', 'to_email', 'to_phone', 'from_name', 'from_email', 'status', 'create_datetime']
    list_filter = ['status']
    search_fields = ['to_name', 'from_name', 'id']
    list_editable = ['status']

    inlines = [
        ShippingFileInline,
    ]
    actions = [export_to_csv]

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            queryset |= self.model.objects.filter(to_name__icontains=search_term)
        else:
            queryset |= self.model.objects.filter(id__exact=search_term_as_int)
        return queryset, may_have_duplicates


@admin.register(ShippingStatus)
class ShippingStatusAdmin(admin.ModelAdmin):
    list_display = ['name']


admin.site.register(ShippingFileType)
