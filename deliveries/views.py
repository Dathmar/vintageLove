from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from pytz import timezone as tz
from datetime import datetime
from .models import Delivery


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_assignments(request):
    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date__gte=
                                         tz('UTC').localize(datetime.now().today()))
    return render(request, 'deliveries.html', {'deliveries': deliveries})


class CreateAssignmentsView(LoginRequiredMixin, View):
    pass