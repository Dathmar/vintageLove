from django import forms
from bespokeShipping.models import Shipping
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


