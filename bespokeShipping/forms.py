from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings


class SizeForm(forms.Form):
    get_static_prefix = settings.STATIC_URL
    size_choices = (('small', mark_safe(f'<img src="{ get_static_prefix }img/small.png" height="150"><br>Small')),
                    ('medium', mark_safe(f'<img src="{ get_static_prefix }img/medium.png" height="150"><br>Medium')),
                    ('large', mark_safe(f'<img src="{ get_static_prefix }img/large.png" height="150"><br>Large')),
                    ('xlarge', mark_safe(f'<img src="{ get_static_prefix }img/x-large.png" height="150"><br>X-Large')))

    size = forms.ChoiceField(widget=forms.RadioSelect(attrs={"onclick": "showTab('#list-to-list')",
                                                             "class": "size-form-check"}),
                             choices=size_choices)


class ShipToForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
                                 max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
                                max_length=200)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                             max_length=200)
    address1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}),
                               max_length=200)
    address2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2'}),
                               max_length=200)
    postal_code = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Postal Code'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}),
                           max_length=200)
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State'}),
                            max_length=200)


class DeliveryLevel(forms.Form):
    shipping_level = (('to_door', 'Delivery to your door.'),
                      ('setup', 'In home delivery and assembly.'))

    level = forms.ChoiceField(widget=forms.RadioSelect(),
                              choices=shipping_level)
