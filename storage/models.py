from django.db import models


# Create your models here.
class Storage(models.Model):
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
