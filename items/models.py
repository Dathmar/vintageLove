from django.db import models


# Create your models here.
class Item(models.Model):
    ITEM_SIZES = (
        ('sm', 'Small'),
        ('md', 'Medium'),
        ('lg', 'Large'),
        ('xl', 'Extra Large')
    )

    size = models.CharField(max_length=2, choices=ITEM_SIZES)
    quantity = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    insured = models.BooleanField(blank=True, null=True)


def item_evidence_path(instance, filename):
    date = instance.schedule_date.strftime('%Y/%m/%d')
    return f'item_evidence/{instance.item.quote}/{date}/{filename}'

'''
class ItemEvidence(models.Model):
    EVIDENCE_TYPE = (
        ('pickup', 'Pickup'),
        ('delivery', 'Delivery')
        ('intake', 'Warehouse Intake'),
        ('output', 'Warehouse Output'),
        ('repair_start', 'Repair Start'),
        ('repair_end', 'Repair Complete'),
        ('repair_checkin', 'Repair Check In')
    )

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    evidence_type = models.TextField(max_length=10, choices=EVIDENCE_TYPE)
    item_evidence = models.FileField(upload_to=item_evidence_path)
'''
