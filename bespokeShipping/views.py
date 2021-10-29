from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def bespoke_shipping_create(request):
    return render(request, 'bespoke_shipping.html')


@login_required
def bespoke_shipping_complete(request):
    return render(request, 'bespoke-shipping-complete.html')