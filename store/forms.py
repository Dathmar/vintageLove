from django import forms


class JoinMovement(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name',
                                                                               'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name',
                                                                              'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email',
                                                            'class': 'form-control'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Subject',
                                                                            'class': 'form-control'}))
    message = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={'placeholder': 'Type your message here...',
                                                                            'class': 'form-control'}))
