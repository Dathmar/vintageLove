from django.contrib import admin
from .models import ServiceTeams, ServiceAreas, Quote, QuoteItem


# Register your models here.
admin.site.register(ServiceTeams)
admin.site.register(ServiceAreas)
admin.site.register(Quote)
admin.site.register(QuoteItem)
