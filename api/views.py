from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required

from deliveries.models import Delivery
from bespokeShipping.models import Shipping, Quote
from django.contrib.auth.models import User

from datetime import datetime

import json
import logging

app_logger = logging.getLogger('app_api')
payment_logger = logging.getLogger('payments')


@login_required
@require_POST
def create_assignment(request):
    body = json.loads(request.body)
    shipping_id = body.get('shipping_id', None)
    scheduled_date = body.get('scheduled_date', None)
    driver = body.get('driver', None)
    pickup = body.get('pickup', None)
    scheduled_time = body.get('scheduled_time', None)

    user = User.objects.get(username=driver)
    shipping = Shipping.objects.get(id=shipping_id)

    try:
        delivery_count = Delivery.objects.filter(
            shipping=shipping,
            scheduled_date=scheduled_date,
            user=user
        ).count()
        delivery = Delivery.objects.create(
            shipping=shipping,
            scheduled_date=scheduled_date,
            user=user,
            pickup=pickup,
            tod=scheduled_time,
            sequence=delivery_count + 1
        )
        delivery.save()

        return JsonResponse({'assignment': delivery.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def update_assignment(request, delivery_id):
    body = json.loads(request.body)

    scheduled_date = body.get('scheduled_date')
    driver = body.get('driver')
    pickup = body.get('pickup')
    scheduled_time = body.get('scheduled_time')

    user = User.objects.get(username=driver)
    scheduled_date = datetime.strptime(scheduled_date, '%Y-%m-%d')

    app_logger.info(scheduled_date)
    app_logger.info(user)

    try:
        delivery = Delivery.objects.get(id=delivery_id)
        shipping = delivery.shipping

        delivery_count = Delivery.objects.filter(
            shipping=shipping,
            scheduled_date=scheduled_date,
            user=user
        ).count()

        delivery.scheduled_date = scheduled_date.date()
        delivery.user = user
        delivery.pickup = pickup
        delivery.tod = scheduled_time
        delivery.sequence = delivery_count + 1
        delivery.save()

        return JsonResponse({'assignment': delivery.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_delivery_table(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    if end_date < start_date:
        tmp = start_date
        start_date = end_date
        end_date = tmp

    if start_date and end_date:
        deliveries = Delivery.objects.filter(scheduled_date__range=[start_date, end_date]).order_by('id')
        t = render_to_string('delivery-table.html', {'deliveries': deliveries})
        return JsonResponse({'table_html': t}, status=200)
    return JsonResponse({'error': 'No date range provided'}, status=400)


@login_required
@require_POST
def approve_quote(request, quote_id):
    try:
        quote = Quote.objects.get(id=quote_id)
        quote.approved = True
        quote.save()
        return JsonResponse({'quote': quote.id}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
