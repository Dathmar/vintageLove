from django import forms
from bespokeShipping.models import Shipping
from .models import EquipmentStatus
from django.contrib.auth.models import User


class DeliverySelectionForm(forms.Form):
    deliveries = forms.ModelMultipleChoiceField(queryset=Shipping.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


class PickupSelectionForm(forms.Form):
    pickups = forms.ModelMultipleChoiceField(queryset=Shipping.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)


class DateDriverForm(forms.Form):
    driver = forms.CharField(label='Driver', max_length=100,
                             widget=forms.Select(
                                 choices=User.objects.filter(groups__name='Driver').values_list('username', 'username')
                             ))
    delivery_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Delivery Date', )


class ShippingAssociateForm(forms.Form):
    sequence = forms.IntegerField(label='Sequence', min_value=1, max_value=100)


class EquipmentStatusForm(forms.ModelForm):
    class Meta:
        model = EquipmentStatus
        fields = ['mileage', 'fuel_level', 'equipment_video']
        widgets = {
            'mileage': forms.NumberInput(attrs={'type': 'number', 'class': 'form-control'}),
            'fuel_level': forms.RadioSelect(attrs={'class': 'form-check'}),
            'equipment_video': forms.FileInput(attrs={'class': 'form-control'}),
        }


