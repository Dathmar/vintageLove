from django.db import models
from .qr_generation import generate_qr_code
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.shortcuts import reverse

import uuid


class ProductStatus(models.Model):
    name = models.CharField(max_length=50)
    available_to_sell = models.BooleanField(default=1)
    disply_wholesale = models.BooleanField(default=0)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'product statuses'


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

    slug = models.SlugField(max_length=4000, blank=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name

    def save(self):
        self.slug = slugify(self.name)
        super(Seller, self).save()

        if not Seller.objects.filter(id=self.id).exists():
            generate_qr_code('https://www.localvintagestore.com/ship/' + str(self.slug),
                             'media/bespoke-shipping/' + str(self.slug) + '_qr.png')

    def get_qr_url(self):
        return '/media/bespoke-shipping/' + str(self.slug) + '_qr.png'


class UserSeller(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)

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

    attributes = models.JSONField(null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def save(self):
        if not self.slug:
            self.slug = slugify(self.title)
            slug_count = Product.objects.filter(slug=self.slug).count() + 1

            if slug_count != 1:
                self.slug = f'{self.slug}-{slug_count}'

        if not Product.objects.filter(id=self.id).exists():
            super(Product, self).save()
            generate_qr_code('https://www.localvintagestore.com/products/' + str(self.id),
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


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images', height_field='image_height', width_field='image_width')
    sequence = models.IntegerField()

    image_height = models.IntegerField(blank=True, null=True)
    image_width = models.IntegerField(blank=True, null=True)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return 'product ' + self.product.title + ' - image ' + str(self.sequence)

    def __repr__(self):
        return self.image.url

