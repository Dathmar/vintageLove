from django import forms

from items.models import Item
from designers.models import Designer
from products.models import Seller


class DesignerForm(forms.Form):
    designer_pays = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input-sm'})
    )
    allow_designer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input-sm'})
    )
    designer_name = forms.CharField(
        widget=(forms.Select(choices=Designer.objects.all().values_list('id', 'name'),
                             attrs={'class': 'form-control-md select2'})),
        required=False
    )


class ToAddressForm(forms.Form):
    to_name = forms.CharField(
        max_length=1000,
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-sm',
            'placeholder': 'Customer Name'})
    )
    to_address = forms.CharField(
        max_length=1000,
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-sm',
            'placeholder': 'Address'})
    )
    to_phone = forms.CharField(
        max_length=1000,
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-sm',
            'placeholder': 'Phone'})
    )
    to_email = forms.EmailField(
        max_length=1000,
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control-sm',
            'placeholder': 'Email'})
    )
    delivery_notes = forms.CharField(
        max_length=2500,
        required=False,
        label=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control-sm',
            'placeholder': 'Delivery Notes'})
    )


class ItemForm(forms.Form):
    pickup = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    delivery = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    receiving = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    storage = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    repair = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    assembly = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    insured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    size = forms.CharField(
        widget=forms.Select(
            choices=Item.ITEM_SIZES,
            attrs={
                'class': 'form-control-sm w-100',
            }
        )
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control-sm w-100',
                'placeholder': 'Quantity',
            }
        )
    )
    description = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm w-100',
                'placeholder': 'Description',
            }
        )
    )
    notes = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control-sm w-100',
                'rows': '3',
                'placeholder': 'Notes',
            }
        )
    )
    custom_from_address = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'form-check-input-sm',
            }
        )
    )
    from_seller = forms.CharField(
        required=False,
        widget=forms.Select(
            choices=Seller.objects.all().values_list('id', 'name'),
            attrs={
                'class': 'form-control-sm select2',
                'placeholder': 'Seller',
            }
        )
    )
    from_address = forms.CharField(
        required=False,
        max_length=1000,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm w-100',
                'placeholder': 'Address',
            }
        )
    )
    pickup_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control-sm',
                'type': 'date',
            }
        )
    )
    delivery_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control-sm',
                'type': 'date',
            }
        )
    )
    length = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Length',
            }
        )
    )
    width = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Width',
            }
        )
    )
    height = forms.CharField(
        required=False,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Height',
            }
        )
    )
    copy_form = forms.CharField(
        required=False,
        widget=forms.Select(
            choices=((1, 1), (2, 2)),
            attrs={
                'title': 'copy data from'
            }
        )
    )


class OverrideForm(forms.Form):
    override_due_now = forms.FloatField(min_value=0, required=False)

