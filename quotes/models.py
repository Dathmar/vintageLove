from django.db import models
from django.conf import settings

from phonenumber_field.modelfields import PhoneNumberField

from products.models import Seller
from designers.models import Designer


# Create your models here.
class Quote(models.Model):
    designer = models.ForeignKey(Designer, on_delete=models.CASCADE, related_name='designer', blank=True, null=True)
    to_name = models.CharField(max_length=1000)
    to_email = models.EmailField(max_length=1000)
    to_address = models.TextField(max_length=1000)
    to_phone = PhoneNumberField(blank=True, null=True)
    due_now = models.DecimalField(max_digits=7, decimal_places=2, default=0)


class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)


class ServiceTeams(models.Model):
    service_team = models.CharField(max_length=50)

    def __str__(self):
        return self.service_team

    class Meta:
        verbose_name_plural = 'Service Teams'


class ServiceAreas(models.Model):
    service_team = models.ForeignKey(ServiceTeams, on_delete=models.CASCADE)
    locality = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.service_team} - {self.locality}'

    class Meta:
        verbose_name_plural = 'Service Areas'
