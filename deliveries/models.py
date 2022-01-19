from django.db import models
from django.conf import settings

from bespokeShipping.models import Shipping


# Create your models here.
class Delivery(models.Model):
    shipping = models.OneToOneField(Shipping, on_delete=models.CASCADE,
                                    limit_choices_to={'status__name__in': ('Order Received', 'Picked Up')})
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    scheduled_date = models.DateField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.shipping} - {self.user} - {self.scheduled_date}'

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'