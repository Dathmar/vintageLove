from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings


class BespokeShippingForm(forms.Form):
    get_static_prefix = settings.STATIC_URL
    size_choices = (('small', mark_safe(f'<img src="{ get_static_prefix }img/small.png" height="150"><br>Small')),
                    ('medium', mark_safe(f'<img src="{ get_static_prefix }img/medium.png" height="150"><br>Medium')),
                    ('large', mark_safe(f'<img src="{ get_static_prefix }img/large.png" height="150"><br>Large')),
                    ('xlarge', mark_safe(f'<img src="{ get_static_prefix }img/x-large.png" height="150"><br>X-Large')))

    size = forms.ChoiceField(widget=forms.RadioSelect(attrs={"onclick": "showTab('#list-to-list')",
                                                             "class": "size-form-check"}),
                             choices=size_choices)

    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name*'}),
                                 max_length=200)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name*'}),
                                 max_length=200)

