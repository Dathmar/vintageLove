from django.db import models
from django.conf import settings

from bespokeShipping.models import Shipping


# Create your models here.
class Delivery(models.Model):
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scheduled_date = models.DateField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
