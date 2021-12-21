from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Delivery


# Create your views here.
@login_required(login_url='/login/?next=/deliveries/')
def my_deliveries(request):
    deliveries = Delivery.objects.filter(user=request.user)
    return render(request, 'deliveries/my-deliveries.html', {'deliveries': deliveries})
