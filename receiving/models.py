from django.db import models


# Create your models here.
class Receiving(models.Model):
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
