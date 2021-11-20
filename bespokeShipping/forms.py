from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings


class FromForm(forms.Form):
    store_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Store Name'}),
                                 label='Store Name', max_length=100)
    store_address_1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}),
                                      label='Address 1', max_length=100)
    store_address_2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2'}),
                                      label='Address 2', max_length=100, required=False)
    store_city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}),
                                 label='City', max_length=100)
    store_state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State'}),
                                  label='State', max_length=100)
    store_postal_code = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Postal Code'}),
                                        label='Postal Code', max_length=100)
    store_phone = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Store Phone'}),
                                  label='Phone', max_length=100)
    store_email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Store Email (optional)'}),
                                   label='Email', max_length=100, required=False)


class SizeForm(forms.Form):
    get_static_prefix = settings.STATIC_URL

    size_small = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'size-form-input', 'style': 'width:75px;',
                                        'placeholder': 'Qty', 'min': '0', 'max': '99'}),
        label=mark_safe(f'<div style="height:150px"><img src="{ get_static_prefix }img/small.png" height="150px"></div><br>Small<br>'))
    size_medium = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'size-form-input', 'style': 'width:75px;',
                                        'placeholder': 'Qty', 'min': '0', 'max': '99'}),
        label=mark_safe(f'<div style="height:150px;"><img src="{ get_static_prefix }img/medium.png" width="225px"></div><br>Medium<br>'))
    size_large = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'size-form-input', 'style': 'width:75px;',
                                        'placeholder': 'Qty', 'min': '0', 'max': '99'}),
        label=mark_safe(f'<div style="height:150px"><img src="{ get_static_prefix }img/large.png" width="175px"></div><br>Large<br>'))
    size_set = forms.CharField(
        widget=forms.NumberInput(attrs={'class': 'size-form-input', 'style': 'width:75px;',
                                        'placeholder': 'Qty', 'min': '0', 'max': '99'}),
        label=mark_safe(f'<div style="height:150px"><img src="{ get_static_prefix }img/ship_set.png" height="150px"></div><br>Set<br>'))

    def clean_size_small(self):
        size_small = self.cleaned_data.get('size_small')
        if size_small < 0:
            raise forms.ValidationError('Enter a positive number.')
        return size_small

    def clean_size_medium(self):
        size_medium = self.cleaned_data.get('size_medium')
        if size_medium < 0:
            raise forms.ValidationError('Enter a positive number.')
        return size_medium

    def clean_size_large(self):
        size_large = self.cleaned_data.get('size_large')
        if size_large < 0:
            raise forms.ValidationError('Enter a positive number.')
        return size_large

    def clean_size_set(self):
        size_set = self.cleaned_data.get('size_set')
        if size_set < 0:
            raise forms.ValidationError('Enter a positive number.')
        return size_set



class ShipToForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
                                 max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
                                max_length=200)
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email'}),
                             max_length=200)
    phone = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Phone'}))
    address1 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 1'}),
                               max_length=200)
    address2 = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Address 2'}),
                               max_length=200, required=False)
    postal_code = forms.CharField(widget=forms.NumberInput(attrs={'placeholder': 'Postal Code'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'City'}),
                           max_length=200)
    state = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'State'}),
                            max_length=200)


class DeliveryLevel(forms.Form):
    get_static_prefix = settings.STATIC_URL
    shipping_level = (('door', mark_safe(f'<img src="{ get_static_prefix }img/to_door.png" height="150"><br/>'
                                         f'Delivery to your door.<br/>(free)')),
                      ('placement', mark_safe(f'<img src="{ get_static_prefix }img/in_home.png" height="150"><br/>'
                                              'In home delivery and placement.<br/>(+$50)')))

    level = forms.ChoiceField(widget=forms.RadioSelect(attrs={"onclick": "showTab('#list-insure-list')"}),
                              choices=shipping_level)


class InsuranceForm(forms.Form):
    get_static_prefix = settings.STATIC_URL
    insurance_level = ((True, mark_safe(f'<img src="{ get_static_prefix }img/free-insurance.png" height="150"><br/>'
                                        f'Insurance up to the value of the shipping service<br/>(free)')),
                       (False, mark_safe(f'<img src="{ get_static_prefix }img/fill-coverage-insurance.png" height="150"><br/>'
                                         f'Full Coverage up to the purchase price of the piece<br/>($50)')))

    insure_level = forms.ChoiceField(widget=forms.RadioSelect(attrs={"onclick": "showTab('#list-submit-list')"}),
                                     choices=insurance_level)
