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
    size_choices = (('small', mark_safe(f'<img src="{ get_static_prefix }img/small.png" height="150"><br>Small')),
                    ('medium', mark_safe(f'<img src="{ get_static_prefix }img/medium.png" height="150"><br>Medium')),
                    ('large', mark_safe(f'<img src="{ get_static_prefix }img/large.png" height="150"><br>Large')),
                    ('set', mark_safe(f'<img src="{ get_static_prefix }img/ship_set.png" height="150"><br>Sets')))

    size = forms.ChoiceField(widget=forms.RadioSelect(attrs={"onclick": "showTab('#list-to-list')",
                                                             "class": "size-form-check"}),
                             choices=size_choices)

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if not size:
            raise forms.ValidationError('Please select a size.')
        return size


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
