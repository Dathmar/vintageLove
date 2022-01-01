from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from pytz import timezone as tz
from datetime import datetime
from .models import Delivery


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_deliveries(request):
    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date__gte=
                                         tz('UTC').localize(datetime.now().today()))
    return render(request, 'deliveries.html', {'deliveries': deliveries})

