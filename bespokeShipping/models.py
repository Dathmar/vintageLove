from django.db import models
from products.models import Seller


# Create your models here.
class Shipping(models.Model):
    size_choices = (('small', 'Small'),
                    ('medium', 'Medium'),
                    ('large', 'Large'),
                    ('set', 'Sets'))
    location_choices = (('door', 'To Door'),
                        ('placement', 'In home placement'))

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    from_name = models.CharField(max_length=1000)
    from_email = models.EmailField(max_length=1000, blank=True, null=True)
    from_address = models.TextField(max_length=1000)
    from_phone = models.CharField(max_length=1000, blank=True, null=True)
    to_name = models.CharField(max_length=1000)
    to_email = models.EmailField(max_length=1000)
    to_address = models.TextField(max_length=1000)
    to_phone = models.CharField(max_length=1000, blank=True, null=True)
    small_quantity = models.IntegerField(default=0, blank=True, null=True)
    media_quantity = models.IntegerField(default=0, blank=True, null=True)
    large_quantity = models.IntegerField(default=0, blank=True, null=True)
    set_quantity = models.IntegerField(default=0, blank=True, null=True)
    ship_location = models.CharField(max_length=10, choices=location_choices)
    insurance = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)
