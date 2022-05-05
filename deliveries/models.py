from django.db import models
from django.conf import settings

from datetime import datetime
from bespokeShipping.models import Shipping

import logging
logger = logging.getLogger('app_api')


# Create your models here.
class Delivery(models.Model):
    window_choices = (('0', '8am-10am'),
                      ('1', '10am-12pm'),
                      ('2', '12pm-2pm'),
                      ('3', '2pm-4pm'),
                      ('4', '4pm-6pm'),
                      ('5', '6pm-8pm'),)

    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    scheduled_date = models.DateField()
    pickup = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=255, default='', blank=True, null=True)
    complete = models.BooleanField(default=False)
    tod = models.CharField(max_length=1, choices=window_choices, null=True, blank=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.shipping} - {self.user} - {self.scheduled_date}'

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'


class Equipment(models.Model):
    name = models.CharField(max_length=255)
    make = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.IntegerField()
    color = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=255)
    purchase_date = models.DateField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.make} - {self.model} - {self.year}'


def equipment_video_path(instance, filename):
    date = instance.schedule_date.strftime('%Y/%m/%d')
    return f'equipment_video/{instance.user.username}/{date}/{instance.timeperiod}/{filename}'


class EquipmentStatus(models.Model):
    time_options = (('morning', 'Morning'),
                    ('evening', 'Evening'),)
    fuel_level_options = (('low', 'Low'),
                          ('quarter', '1/4'),
                          ('half', '1/2'),
                          ('three_quarter', '3/4'),
                          ('full', 'Full'),)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timeperiod = models.CharField(max_length=10, choices=time_options)
    schedule_date = models.DateField()

    # should add later when we start using actual usernames vs the equipment name.
    # equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    mileage = models.FloatField(default=0)
    fuel_level = models.CharField(max_length=20, choices=fuel_level_options, blank=False, default='Unspecified')
    equipment_video = models.FileField(upload_to=equipment_video_path)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.timeperiod} - {self.schedule_date}'

    class Meta:
        verbose_name = 'Daily Equipment Status'
        verbose_name_plural = 'Daily Equipment Statuses'

