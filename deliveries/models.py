from django.db import models
from django.conf import settings

from bespokeShipping.models import Shipping


# Create your models here.
class Delivery(models.Model):
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    scheduled_date = models.DateField()
    pickup = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, default='', blank=True, null=True)
    complete = models.BooleanField(default=False)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.shipping} - {self.user} - {self.scheduled_date}'

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
