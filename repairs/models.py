from django.db import models

from items.models import Item


# Create your models here.
class Repair(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    notes = models.CharField(max_length=255, blank=True, null=True)


class RepairQuote(models.Model):
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    quote_price = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    paid_date = models.DateField(blank=True, null=True)
    approved_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def materials_cost(self):
        return RepairMaterials.objects.filter(repair=self).aggregate(total=models.Sum('cost'))['total']


class RepairMaterials(models.Model):
    repair = models.ForeignKey(Repair, on_delete=models.CASCADE)
    material = models.CharField(max_length=255)
    quantity = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(max_length=255, blank=True, null=True)

