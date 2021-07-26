from django.db import models
from .qr_generation import generate_qr_code
from django.contrib.auth.models import User
import uuid



class ProductStatus(models.Model):
    name = models.CharField(max_length=50)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name


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
    name = models.CharField(max_length=4000)
    street = models.CharField(max_length=4000)
    city = models.CharField(max_length=4000)
    state = models.CharField(max_length=4000)
    zip = models.CharField(max_length=4000)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.name


class UserSeller(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=4000)
    description = models.CharField(max_length=8000)
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, default=1)

    dimension_width = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_height = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_length = models.DecimalField(max_digits=7, decimal_places=2)
    dimension_weight = models.DecimalField(max_digits=7, decimal_places=2)

    purchase_price = models.DecimalField(max_digits=7, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=7, decimal_places=2)
    retail_price = models.DecimalField(max_digits=7, decimal_places=2)
    origin = models.CharField(max_length=4000)

    status = models.ForeignKey(ProductStatus, default=1, on_delete=models.PROTECT)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def save(self):
        if not Product.objects.filter(id=self.id).exists():
            super(Product, self).save()
            generate_qr_code('https://www.localvintagestore.com/products/' + str(self.id),
                             'media/qr_img/' + str(self.id) + '_qr.png')
        else:
            super(Product, self).save()

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')
    sequence = models.IntegerField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return 'product ' + self.product.title + ' - image ' + str(self.sequence)

