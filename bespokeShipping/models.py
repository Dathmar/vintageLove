from django.db import models
from products.models import Seller
from base.Emailing import send_ship_status_email, send_internal_shipping_notification, quote_notification_email
from base.texting import quote_notification_text
from phonenumber_field.modelfields import PhoneNumberField
import uuid
import base62
from random import getrandbits
import logging

logger = logging.getLogger('app_api')

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
    from_phone = PhoneNumberField(blank=True, null=True)
    to_name = models.CharField(max_length=1000)
    to_email = models.EmailField(max_length=1000)
    to_address = models.TextField(max_length=1000)
    to_phone = PhoneNumberField(blank=True, null=True)
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
    notes = models.TextField(max_length=4000, blank=True, null=True)
    requested_date = models.DateField(blank=True, null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def description(self):
        description = ''
        if self.small_description:
            description += f' {self.small_description}'
        if self.medium_description:
            description += f' {self.medium_description}'
        if self.large_description:
            description += f' {self.large_description}'
        if self.set_description:
            description += f' {self.set_description}'

        return description

    def item_count(self):
        return self.small_quantity + self.medium_quantity + self.large_quantity + self.set_quantity

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
        return f'{self.id}'

    class Meta:
        ordering = ['-create_datetime']


class Quote(models.Model):
    size_choices = (('small', 'Small'),
                    ('medium', 'Medium'),
                    ('large', 'Large'),
                    ('set', 'Sets'))
    location_choices = (('door', 'To Door'),
                        ('placement', 'In home placement'))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    from_name = models.CharField(max_length=1000)
    from_email = models.EmailField(max_length=1000, blank=True, null=True)
    from_address = models.TextField(max_length=1000)
    from_phone = PhoneNumberField(blank=True, null=True)
    to_name = models.CharField(max_length=1000)
    to_email = models.EmailField(max_length=1000)
    to_address = models.TextField(max_length=1000)
    to_phone = PhoneNumberField(blank=True, null=True)
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
    paid = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, blank=True, null=True)

    requested_date = models.DateField(blank=True, null=True)

    notes = models.TextField(max_length=4000, blank=True, null=True)
    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    encoding = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f'{self.id} {self.to_name}'

    def save(self, *args, **kwargs):
        if not Quote.objects.filter(id=self.id).exists():
            base = base62.encodebytes(self.id.bytes)
            self.encoding = self.generate_unique_encoding()
            quote_notification_email(self)
            quote_notification_text(self)

        if self.approved and not self.shipping:
            init_status = ShippingStatus.objects.get(name='Order Received')
            shipping = Shipping.objects.create(
                seller=self.seller,
                from_name=self.from_name,
                from_email=self.from_email,
                from_address=self.from_address,
                from_phone=self.from_phone,
                to_name=self.to_name,
                to_email=self.to_email,
                to_address=self.to_address,
                to_phone=self.to_phone,
                small_quantity=self.small_quantity,
                medium_quantity=self.medium_quantity,
                large_quantity=self.large_quantity,
                set_quantity=self.set_quantity,
                small_description=self.small_description,
                medium_description=self.medium_description,
                large_description=self.large_description,
                set_description=self.set_description,
                ship_location=self.ship_location,
                insurance=self.insurance,
                cost=self.cost,
                distance=self.distance,
                status=init_status,
                requested_date=self.requested_date,
                notes=self.notes,
            )
            shipping.save()
            self.shipping = shipping

        super(Quote, self).save()

    def description(self):
        description = ''
        if self.small_description:
            description += f' {self.small_description}'
        if self.medium_description:
            description += f' {self.medium_description}'
        if self.large_description:
            description += f' {self.large_description}'
        if self.set_description:
            description += f' {self.set_description}'
        return description

    def item_count(self):
        logger.info(f'{self.small_quantity} {self.medium_quantity} {self.large_quantity} {self.set_quantity}')
        logger.info(self.small_quantity + self.medium_quantity + self.large_quantity + self.set_quantity)
        return self.small_quantity + self.medium_quantity + self.large_quantity + self.set_quantity

    def generate_unique_encoding(self):
        while True:
            base = base62.encodebytes(self.id.bytes + getrandbits(8).to_bytes(1, 'big'))
            base = base[:6].zfill(6)
            if not Quote.objects.filter(encoding=base).exists():
                return base

    class Meta:
        ordering = ['-create_datetime']


class ShippingFileType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def get_shipping_upload_path(instance, filename):
    return f'shipping_files/{instance.shipping.id}/{filename}'


class ShippingFile(models.Model):
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE)
    type = models.ForeignKey(ShippingFileType, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_shipping_upload_path)

    def __str__(self):
        return f'{self.shipping.id} {self.file.name}'

    class Meta:
        ordering = ['-shipping__create_datetime']

