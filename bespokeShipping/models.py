from django.db import models
from products.models import Seller
from base.Emailing import send_ship_status_email, send_internal_shipping_notification


class ShippingStatus(models.Model):
    name = models.CharField(max_length=1000, unique=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Shipping Statuses'


# Create your models here.
class Shipping(models.Model):
    size_choices = (('small', 'Small'),
                    ('medium', 'Medium'),
                    ('large', 'Large'),
                    ('set', 'Sets'))
    location_choices = (('door', 'To Door'),
                        ('placement', 'In home placement'))
    window_choices = (('morning', 'Morning'),
                      ('mid-day', 'Mid-day'),
                      ('afternoon', 'Afternoon'),
                      ('evening', 'Evening'))


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
    medium_quantity = models.IntegerField(default=0, blank=True, null=True)
    large_quantity = models.IntegerField(default=0, blank=True, null=True)
    set_quantity = models.IntegerField(default=0, blank=True, null=True)
    small_description = models.TextField(max_length=1000, blank=True, null=True)
    medium_description = models.TextField(max_length=1000, blank=True, null=True)
    large_description = models.TextField(max_length=1000, blank=True, null=True)
    set_description = models.TextField(max_length=1000, blank=True, null=True)
    ship_location = models.CharField(max_length=10, choices=location_choices)
    insurance = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    status = models.ForeignKey(ShippingStatus, on_delete=models.CASCADE, blank=True, null=True)
    order_window = models.CharField(max_length=10, choices=window_choices, blank=True, null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def save(self, *args, **kwargs):
        if not Shipping.objects.filter(id=self.id).exists():
            to_status = 'created'
            send_ship_status_email(self, to_status=to_status)
            send_internal_shipping_notification(self)
        else:
            last_status = Shipping.objects.get(id=self.id).status
            if last_status != self.status:
                to_status = self.status.name
                send_ship_status_email(self, to_status=to_status)

        super(Shipping, self).save()

    def __str__(self):
        return f'{self.id} {self.to_name}'

    class Meta:
        ordering = ['-create_datetime']
