from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address1', 'address2', 'postal_code', 'city', 'state']
        widgets = {
            'state': forms.TextInput(attrs={'onChange': 'getCost()'})
        }
