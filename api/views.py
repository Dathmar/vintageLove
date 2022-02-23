from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string

from deliveries.models import Delivery

import logging

logger = logging.getLogger('app_api')


# Create your views here.
def get_delivery_table(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    start_date = timezone.strptime(start_date, '%Y-%m-%d')
    end_date = timezone.strptime(end_date, '%Y-%m-%d')

    if end_date < start_date:
        tmp = start_date
        start_date = end_date
        end_date = tmp

    logger.info('start_date: {}'.format(start_date))
    logger.info('end_date: {}'.format(end_date))

    if start_date and end_date:
        deliveries = Delivery.objects.filter(scheduled_date__range=[start_date, end_date]).order_by('id')
        t = render_to_string('delivery-table.html', {'deliveries': deliveries})
        return JsonResponse({'table_html': t}, status=200)
    return JsonResponse({'error': 'No date range provided'}, status=400)