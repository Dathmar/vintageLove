from django.db import models
from products.models import Product
from django.conf import settings


# Create your models here.
class UserFolders(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    is_public = models.BooleanField(default=False)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    class Meta:
        unique_together = ['user', 'name']
        verbose_name_plural = 'User Folders'

    def get_absolute_url(self):
        return f'/folders/{self.name}'

    def __str__(self):
        return f'{self.user} - {self.name}'


class FolderContents(models.Model):
    folder = models.ForeignKey(UserFolders, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)
