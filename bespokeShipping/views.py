from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import SizeForm, ShipToForm, DeliveryLevel
from products.models import UserSeller, Seller


# Create your views here.
def create(request, seller_slug=None):
    if seller_slug:
        seller = get_object_or_404(Seller, slug=seller_slug)
    elif seller_slug == 'unknown':
        from_form = FromForm()
    else:
        seller = get_object_or_404(UserSeller, user=request.user).seller

    size_form = SizeForm()
    ship_to_form = ShipToForm()
    delivery_level = DeliveryLevel()
    context = {
        'size_form': size_form,
        'ship_to_form': ship_to_form,
        'delivery_level': delivery_level,
        'seller': seller,
        'hide_subscribe': True,
    }
    return render(request, 'bespoke_shipping.html', context)


def complete(request):
    return render(request, 'bespoke-shipping-complete.html')
