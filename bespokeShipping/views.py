from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import SizeForm, ShipToForm, DeliveryLevel


# Create your views here.
@login_required
def create(request, store_id=None):
    size_form = SizeForm()
    ship_to_form = ShipToForm()
    delivery_level = DeliveryLevel()
    context = {
        'size_form': size_form,
        'ship_to_form': ship_to_form,
        'delivery_level': delivery_level,
    }
    return render(request, 'bespoke_shipping.html', context)


@login_required
def complete(request):
    return render(request, 'bespoke-shipping-complete.html')
