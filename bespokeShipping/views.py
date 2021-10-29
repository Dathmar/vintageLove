from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BespokeShippingForm


# Create your views here.
@login_required
def bespoke_shipping_create(request):
    shipping_form = BespokeShippingForm()
    context = {
        'form': shipping_form
    }
    return render(request, 'bespoke_shipping.html', context)


@login_required
def bespoke_shipping_complete(request):
    return render(request, 'bespoke-shipping-complete.html')