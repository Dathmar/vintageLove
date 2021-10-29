from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SizeForm, ShipToForm


# Create your views here.
@login_required
def bespoke_shipping_create(request):
    size_form = SizeForm()
    ship_to_form = ShipToForm()
    context = {
        'size_form': size_form,
        'ship_to_form': ship_to_form,
    }
    return render(request, 'bespoke_shipping.html', context)


@login_required
def bespoke_shipping_complete(request):
    return render(request, 'bespoke-shipping-complete.html')