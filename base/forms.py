from django import forms


class OrderCreateForm(forms.ModelForm):
    class Meta:
        widgets = {
            'email': forms.EmailField(attrs={'placeholder': "Yes, here's my email"})
        }
