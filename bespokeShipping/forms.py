from django import forms


class BespokeShippingForm(forms.ModelForm):
    size_choices = (('small', 'Small'),
                    ('medium', 'Medium'),
                    ('large', 'Large'),
                    ('xlarge', 'X-Large'))

    size = forms.RadioSelect(choices=size_choices, attrs={"onclick: showTab('#list-to-list')"})