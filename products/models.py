from django.db import models
from .qr_generation import generate_qr_code
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

import uuid
import os

from .image_generation import gen_resize, rotate_image
import logging

logger = logging.getLogger('app_api')


class ProductStatus(models.Model):
    name = models.CharField(max_length=50)
    available_to_sell = models.BooleanField(default=1)
    display_wholesale = models.BooleanField(default=0)
    display_order = models.IntegerField(default=0)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'product statuses'
        ordering = ['display_order']


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'


class Seller(models.Model):
    name = models.CharField(max_length=4000, unique=True)
    street = models.CharField(max_length=4000)
    city = models.CharField(max_length=4000)
    state = models.CharField(max_length=4000)
    zip = models.CharField(max_length=4000)
    email = models.EmailField(max_length=254, blank=True, null=True)
    phone = models.CharField(max_length=4000, blank=True, null=True)

    slug = models.SlugField(max_length=4000, blank=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self):
        if not self.slug:
            slug_base = slugify(self.name + " " + self.city)
            slug = slug_base
            count = 0
            while Seller.objects.filter(slug=slug).exists():
                count += 1
                slug = f'{slug_base}-{count}'

            self.slug = slug

        if not Seller.objects.filter(id=self.id).exists():
            super(Seller, self).save()
            generate_qr_code('https://www.globalvintagelove.com/ship/location/' + str(self.slug),
                             'media/bespoke-shipping/' + str(self.slug) + '_qr.png')
        else:
            super(Seller, self).save()

    def get_qr_url(self):
        return '/media/bespoke-shipping/' + str(self.slug) + '_qr.png'


class UserSeller(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)

    # think about adding automated user seller creation based on new group (auto-user seller)

    def __str__(self):
        return f'User {self.user.first_name} {self.user.last_name} -- Seller {self.seller.name}'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=4000)
    slug = models.SlugField(max_length=4000, unique=True, null=False)
    description = models.CharField(max_length=8000)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)

    dimension_width = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_height = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_length = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_weight = models.DecimalField(max_digits=7, decimal_places=2)

    purchase_price = models.DecimalField(max_digits=7, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=7, decimal_places=2)
    retail_price = models.DecimalField(max_digits=7, decimal_places=2)
    origin = models.CharField(max_length=4000)

    status = models.ForeignKey(ProductStatus, default=1, on_delete=models.PROTECT)

    attributes = models.JSONField(null=True, blank=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = slugify(self.title)
            slug = slug_base
            count = 0
            while Product.objects.filter(slug=slug).exists():
                count += 1
                slug = f'{slug_base}-{count}'

            self.slug = slug

        if not Product.objects.filter(id=self.id).exists():
            super(Product, self).save()
            generate_qr_code('https://www.globalvintagelove.com/products/' + str(self.id),
                             'media/qr_img/' + str(self.id) + '_qr.png')
        else:
            super(Product, self).save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:product-slug', kwargs={'product_slug': self.slug})

    def get_qr_url(self):
        return '/media/qr_img/' + str(self.id) + '_qr.png'

    class Meta:
        ordering = ['create_datetime']


class ProductCategory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.product.title} - {self.category.name}'

    class Meta:
        ordering = ['id']
        unique_together = [['product', 'category']]
        verbose_name_plural = 'Product Categories'


def product_image_upload(instance, filename):
    if instance.image_size == 0:
        return f'product_images/original/{filename}'
    return f'product_images/thumbnail/{filename}'


class ProductImage(models.Model):
    image_size_choices = ((0, 'original'), (1, 'thumbnail'))

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_size = models.IntegerField(choices=image_size_choices, default=0)
    image = models.ImageField(upload_to=product_image_upload, height_field='image_height', width_field='image_width')
    sequence = models.IntegerField()

    image_height = models.IntegerField(blank=True, null=True)
    image_width = models.IntegerField(blank=True, null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return 'product ' + self.product.title + ' - image ' + str(self.sequence)

    def __repr__(self):
        return self.image.url


@receiver(post_save, sender=ProductImage, dispatch_uid="update_product_image")
def update_image(sender, instance, **kwargs):
    if instance.image:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fullpath = BASE_DIR + instance.image.url
        try:
            rotate_image(fullpath)
            if instance.image_size == 0:
                height_max = 500
                width_max = 400
                new_img = gen_resize(instance.image.path, (height_max, width_max))
                new_img_path = os.path.join('product_images/thumbnail/',
                                            os.path.basename(instance.image.path))
                new_img.save(os.path.join(settings.MEDIA_ROOT, new_img_path))

                if not ProductImage.objects.filter(product=instance.product,
                                                   image_size=1,
                                                   image__iendswith=os.path.basename(instance.image.path)).exists():
                    logger.info(f'creating thumbnail image for {instance.image.path}')
                    new_product_image = ProductImage.objects.create(
                        product=instance.product,
                        image_size=1,
                        image=new_img_path,
                        sequence=instance.sequence,
                    )

                    new_product_image.save()
        except Exception as e:
            logger.info(f'error rotating image {fullpath}')
            logger.info(e)


class Attribute(models.Model):
    name = models.CharField(max_length=4000)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=4000)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.value


class HomepageProducts(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True,
                                   limit_choices_to={'status__available_to_sell': 'True'})
    sequence = models.IntegerField(unique=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.product.title

    class Meta:
        ordering = ['sequence']
        verbose_name_plural = 'Homepage Products'

