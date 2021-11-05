from django.shortcuts import render, get_object_or_404
from .forms import SizeForm, ShipToForm, DeliveryLevel, FromForm
from products.models import UserSeller, Seller
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Shipping

from orders.views import submit_payment
from base.Emailing import EmailThread

import json
import googlemaps
import uuid


# Create your views here.
def create(request, seller_slug=None):
    if not request.session.get('idempotency_shipping_key'):
        request.session['idempotency_shipping_key'] = str(uuid.uuid4())

    if request.method == 'POST':
        size_form = SizeForm(request.POST)
        ship_to_form = ShipToForm(request.POST)
        delivery_level = DeliveryLevel(request.POST)

        seller = None

        if seller_slug == 'unknown':
            from_form = FromForm(request.POST)
            if from_form.is_valid():
                from_name = from_form.cleaned_data['store_name']
                from_address1 = from_form.cleaned_data['store_address_1']
                from_address2 = from_form.cleaned_data['store_address_2']
                from_city = from_form.cleaned_data['store_city']
                from_state = from_form.cleaned_data['store_state']
                from_postal_code = from_form.cleaned_data['store_postal_code']
                from_phone = from_form.cleaned_data['store_phone']
                from_email = from_form.cleaned_data['store_email']

                from_address = from_address1
                if from_address2:
                    from_address += '\n' + from_address2
                from_address += '\n' + from_city + ', ' + from_state + ' ' + from_postal_code
            else:
                context = {
                    'size_form': size_form,
                    'ship_to_form': ship_to_form,
                    'delivery_level': delivery_level,
                    'seller': seller,
                    'hide_subscribe': True,
                    'square_js_url': settings.SQUARE_JS_URL,
                    'from_form': from_form,
                }
                return render(request, 'bespoke_shipping.html', context)

        elif seller_slug:
            seller = get_object_or_404(Seller, slug=seller_slug)
        else:
            seller = get_object_or_404(UserSeller, user=request.user).seller

        if seller:
            from_address = seller.street + '\n' + seller.city + ', ' + seller.state + ' ' + seller.zip
            from_name = seller.name
            from_email = seller.email
            from_phone = seller.phone

        if size_form.is_valid() and ship_to_form.is_valid():
            size = size_form.cleaned_data['size']

            ship_to_first_name = ship_to_form.cleaned_data['first_name']
            ship_to_last_name = ship_to_form.cleaned_data['last_name']
            ship_to_address1 = ship_to_form.cleaned_data['address1']
            ship_to_address2 = ship_to_form.cleaned_data['address2']
            ship_to_city = ship_to_form.cleaned_data['city']
            ship_to_state = ship_to_form.cleaned_data['state']
            ship_to_postal_code = ship_to_form.cleaned_data['postal_code']
            ship_to_email = ship_to_form.cleaned_data['email']

            ship_to_address = ship_to_address1
            if ship_to_address2:
                ship_to_address += '\n' + ship_to_address2
            ship_to_address += '\n' + ship_to_city + ', ' + ship_to_state + ' ' + ship_to_postal_code

            shipping_level = delivery_level.cleaned_data['shipping_level']

            cost, distance = calculate_shipping_cost(size, from_address, ship_to_address, shipping_level)

            # now charge the card
            charge_cost = cost * 100
            idempotency_key = request.session.get('idempotency_shipping_key')
            nonce = request.session.get('nonce')

            payment_result = submit_payment(charge_cost, nonce, idempotency_key)
            request.session['idempotency_shipping_key'] = False

            if payment_result == 'pass':
                # now create the shipping
                shipping = Shipping.objects.create(seller=seller,
                                                   from_name=from_name,
                                                   from_address=from_address,
                                                   from_email=from_email,
                                                   from_phone=from_phone,
                                                   to_name=ship_to_first_name + ' ' + ship_to_last_name,
                                                   to_address=ship_to_address,
                                                   ship_size=size,
                                                   ship_location=shipping_level,
                                                   cost=cost,
                                                   distance=distance)
                shipping.save()

                send_internal_shipping_notification(shipping)

                render(request, 'bespoke_shipping_complete.html', {'shipping': shipping})
            else:
                context = {
                    'size_form': size_form,
                    'ship_to_form': ship_to_form,
                    'delivery_level': delivery_level,
                    'seller': seller,
                    'hide_subscribe': True,
                    'square_js_url': settings.SQUARE_JS_URL,
                }

                if from_form:
                    context.update({'from_form': from_form})
                return render(request, 'bespoke_shipping.html', context)
        else:
            context = {
                'size_form': size_form,
                'ship_to_form': ship_to_form,
                'delivery_level': delivery_level,
                'seller': seller,
                'hide_subscribe': True,
                'square_js_url': settings.SQUARE_JS_URL,
            }

            if from_form:
                context.update({'from_form': from_form})
            return render(request, 'bespoke_shipping.html', context)
    from_form = None
    if seller_slug == 'unknown':
        from_form = FromForm()
        seller = None
    elif seller_slug:
        seller = get_object_or_404(Seller, slug=seller_slug)
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
        'square_js_url': settings.SQUARE_JS_URL,
    }

    if from_form:
        context.update({'from_form': from_form})
    return render(request, 'bespoke_shipping.html', context)


def complete(request):
    return render(request, 'bespoke-shipping-complete.html')


def ship_cost(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        ship_size = body['ship_size']
        from_address = body['from_address']
        to_address = body['to_address']
        to_door = body['to_door']
        try:
            cost, distance = calculate_shipping_cost(ship_size, from_address, to_address, to_door)
            return JsonResponse({'cost': cost, 'distance': str(distance)})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return HttpResponseNotAllowed(['POST', ])


def calculate_shipping_cost(ship_size, from_address, to_address, to_door):
    distance = calculate_distance(from_address, to_address)
    distance = float(distance.split(' ')[0])

    if distance <= 50:
        distance_range = '0-50'
    elif distance <= 100:
        distance_range = '51-100'
    elif distance <= 150:
        distance_range = '101-150'
    elif distance <= 200:
        distance_range = '151-200'
    elif distance <= 250:
        distance_range = '201-250'
    else:
        distance_range = '251'

    shipping_chart = {
        'small': {
            '0-50': 50,
            '51-100': 75,
            '101-150': 85,
            '151-200': 100,
            '201-250': 100,
            '251': 100
        },
        'medium': {
            '0-50': 75,
            '51-100': 100,
            '101-150': 125,
            '151-200': 150,
            '201-250': 150,
            '251': 150
        },
        'large': {
            '0-50': 150,
            '51-100': 200,
            '101-150': 250,
            '151-200': 300,
            '201-250': 300,
            '251': 300
        },
        'set': {
            '0-50': 250,
            '51-100': 300,
            '101-150': 350,
            '151-200': 500,
            '201-250': 500,
            '251': 500
        },
    }
    cost = shipping_chart[ship_size][distance_range]
    if to_door:
        cost += 50

    return cost, distance


def calculate_distance(from_address, to_address):
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    try:
        address1 = gmaps.geocode(address=from_address)
        address2 = gmaps.geocode(address=to_address)

        address1_place_id = 'place_id:' + address1[0]['place_id']
        address2_place_id = 'place_id:' + address2[0]['place_id']

        distance = gmaps.distance_matrix(address1_place_id, address2_place_id, mode='driving', units='imperial', )

        return distance['rows'][0]['elements'][0]['distance']['text']
    except Exception as e:
        raise e


def send_internal_shipping_notification(shipping):
    subject = f'New Shipping Order Received for {shipping.from_name}'

    if settings.ENVIRONMENT == 'localhost':
        subject = f'!!TESTING!! - {subject}'

    body = f'''
        We have a new shipping order

        Shipping Origin
        Name: {shipping.from_name}
        E-mail: {shipping.from_email}
        Phone: {shipping.from_phone}
        Address:
        {shipping.from_address}

        Shipping Destination
        Name: {shipping.to_name}
        E-mail: {shipping.to_email}
        Phone: {shipping.to_phone}
        Address:
        {shipping.to_address}
        
        '''

    html_body = f"""
                    <!DOCTYPE html>
                    <html>
                        <head>
                        </head>
                        <body>
                            <p>We have a new shipping order</p>
                            <p></p>
                            <p>Shipping Origin</p>
                            <p>Name: {shipping.from_name}</p>
                            <p>E-mail: {shipping.from_email}</p>
                            <p>Phone: {shipping.from_phone}</p>
                            <p>Address:</p>
                            <p>{shipping.from_address}</p>
                            <p></p>
                            <p>Shipping Destination</p>
                            <p>Name: {shipping.to_name}</p>
                            <p>E-mail: {shipping.to_email}</p>
                            <p>Phone: {shipping.to_phone}</p>
                            <p>Address:</p>
                            <p>{shipping.to_address}</p>
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
