from django.db import models
from products.models import Product

# Create your models here.
class UserFolders(models.Model):
    name = models.CharField(max_length=50)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)