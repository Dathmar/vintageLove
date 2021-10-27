import uuid
import json
from base.Emailing import EmailThread

from django.shortcuts import render
from .models import OrderItem, Order
from .forms import OrderCreateForm
from products.models import Product, ProductStatus
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required

from datetime import datetime
from decimal import Decimal

from square.client import Client


# Create your views here.
def order_create(request, product_id):
    order_item = Product.objects.filter(pk=product_id).first()
    sold_status = ProductStatus.objects.filter(name='Sold').first()

    payment_result = ''

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            if order_item.status != sold_status:
                state = form.cleaned_data['state']
                order_cost_info = get_order_cost_info(state, order_item.retail_price)

                payment_result = submit_payment(order_cost_info['order_cost'] * 100, request.session['nonce'],
                                                request.session['idempotency_key'])
                request.session['idempotency_key'] = False

                if payment_result == 'pass':
                    order = form.save()
                    order.paid = True
                    order.save()

                    OrderItem.objects.create(order=order, product=order_item, price=order_item.retail_price, quantity=1)

                    order_item.status = ProductStatus.objects.filter(name='Sold').first()
                    order_item.update_datetime = datetime.now()
                    order_item.save()

                    # send notification e-mails need to add Mailchimp e-mail
                    send_internal_order_notification(order)

                    return render(request, 'orders/order/created.html', {'order': order})
            else:
                form = OrderCreateForm()
    else:
        form = OrderCreateForm()

    if not request.session.get('idempotency_key'):
        request.session['idempotency_key'] = str(uuid.uuid4())

    data = {
        'form': form,
        'product_id': product_id,
        'product': order_item,
        'shipping_amount': '0.00',
        'square_js_url': settings.SQUARE_JS_URL,
        'payment_errors': payment_result,
        'key': request.session['idempotency_key'],
    }
    return render(request, 'orders/order/create.html', data)


def send_internal_order_notification(order):
    subject = f'New Online Order Received for {order.first_name} {order.last_name}'

    if settings.ENVIRONMENT == 'localhost':
        subject = f'!!TESTING!! - {subject}'

    item = OrderItem.objects.filter(order=order).first()
    order_item = item.product.title

    body = f'''
    We have a new order
    
    Order info:
    Name: {order.first_name} {order.last_name}
    E-mail: {order.email}
    Address:
    {order.address1}
    {order.address2}
    {order.city}, {order.state} {order.postal_code}
    
    Ordered item: {order_item}
    Paid: {order.get_total_cost}
    '''

    html_body = f"""
                <!DOCTYPE html>
                <html>
                    <head>
                    </head>
                    <body>
                        <p>We have a new order</p>
                        <p></p>
                        <p>Order info:</p>
                        <p>Name: {order.first_name} {order.last_name}</p>
                        <p>E-mail: {order.email}</p>
                        <p>Address:</p>
                        <p>{order.address1}</p>
                        <p>{order.address2}</p>
                        <p>{order.city}, {order.state} {order.postal_code}</p>
                        <p>Ordered item: {order_item}</p>
                        <p>Paid: {order.get_total_cost()}</p>
                    </body>
                </html>
                """

    EmailThread(
        subject=subject,
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient=settings.EMAIL_HOST_USER,
        fail_silently=False,
        html_message=html_body
    ).start()


def get_order_cost_info(state, cost):
    tax_value = get_tax(state)
    shipping_amount = 0

    total_tax = round(Decimal((cost + shipping_amount) * Decimal(tax_value / Decimal(100))), 2)
    price_with_tax = round(Decimal(cost + shipping_amount + total_tax), 2)

    return {
        'shipping_amount': str(shipping_amount),
        'tax_percent': str(tax_value),
        'tax_amount': str(total_tax),
        'order_cost': price_with_tax,
    }


def square_app_id(request):
    data = {
        'square_app_id': settings.SQUARE_APP_ID,
    }
    return JsonResponse(data, safe=False)


def order_cost(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        product = Product.objects.filter(pk=body['product_id']).first()

        if product.status.name == 'Sold':
            data = {
                'tax_value': 'NA',
                'total_tax': 'NA',
                'order_cost': 'Not Available',
            }
        else:
            state = body['state']
            tax_value = get_tax(state)
            cost = product.retail_price

            data = get_order_cost_info(state, cost)

        return JsonResponse(data, safe=False)

    return HttpResponseNotAllowed(['POST', ])


def get_tax(state):
    tax = Decimal(0.00)
    if state.strip().lower() in ('tx', 'texas'):
        tax = Decimal(8.25)

    return tax


def order_nonce(request):
    if request.method == 'POST':
        request.session['nonce'] = json.loads(request.body)['nonce']
        return HttpResponse('ok')

    return HttpResponseNotAllowed(['POST', ])


def submit_payment(payment_amount, nonce, idempotency_key):
    # process the payment
    body = {
        'source_id': nonce,
        'idempotency_key': f'{str(idempotency_key)}',
        'amount_money': {
            'amount': int(payment_amount),
            'currency': 'USD'
        }
    }

    client = Client(
        access_token=settings.SQUARE_ACCESS_TOKEN,
        environment=settings.SQUARE_ENVIRONMENT,
    )

    payments_api = client.payments
    result = payments_api.create_payment(body)

    if result.is_success():
        return 'pass'
    elif result.is_error():
        payment_errors = []
        for error in result.errors:
            payment_errors.append(error['detail'])

        return payment_errors


@login_required
def bespoke_shipping(request):
    return render(request, 'orders/bespoke_shipping.html')


@login_required
def bespoke_shipping_complete(request):
    return render(request, 'orders/bespoke-shipping-complete.html')
