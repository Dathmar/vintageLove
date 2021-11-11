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
    from_form = None
    if not request.session.get('idempotency_shipping_key'):
        request.session['idempotency_shipping_key'] = str(uuid.uuid4())

    if request.method == 'POST':
        size_form = SizeForm(request.POST)
        ship_to_form = ShipToForm(request.POST)
        delivery_level = DeliveryLevel(request.POST)

        seller = None
        from_form_valid = True
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
                from_form_valid = False
        elif seller_slug:
            seller = get_object_or_404(Seller, slug=seller_slug)
        else:
            seller = get_object_or_404(UserSeller, user=request.user).seller

        if seller:
            from_address = seller.street + '\n' + seller.city + ', ' + seller.state + ' ' + seller.zip
            from_name = seller.name
            from_email = seller.email
            from_phone = seller.phone

        if size_form.is_valid() and ship_to_form.is_valid() and delivery_level.is_valid() and from_form_valid:
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

            shipping_level = delivery_level.cleaned_data['level']

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
                                                   to_email=ship_to_email,
                                                   ship_size=size,
                                                   ship_location=shipping_level,
                                                   cost=cost,
                                                   distance=distance)
                shipping.save()

                send_internal_shipping_notification(shipping)

                return render(request, 'bespoke_shipping_complete.html', {'shipping': shipping})
            else:
                context = {
                    'size_form_errors': size_form.errors,
                    'size_form': size_form,
                    'ship_to_form_errors': ship_to_form.errors,
                    'ship_to_form': ship_to_form,
                    'delivery_level': delivery_level,
                    'delivery_level_errors': delivery_level.errors,
                    'seller': seller,
                    'hide_subscribe': True,
                    'square_js_url': settings.SQUARE_JS_URL,
                    'paymen_errors': payment_result
                }

                if from_form:
                    context.update({'from_form': from_form, 'from_form_errors': from_form.errors})
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
            cost, distance, supported_state = calculate_shipping_cost(ship_size, from_address, to_address, to_door)
            return JsonResponse({'cost': cost, 'distance': str(distance), 'supported_state': supported_state})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return HttpResponseNotAllowed(['POST', ])


def calculate_shipping_cost(ship_size, from_address, to_address, to_door):
    distance, to_state, from_state = calculate_distance(from_address, to_address)
    distance = float(distance.split(' ')[0].replace(',', ''))

    if to_state.casefold() not in ['tx', 'texas'] or from_state.casefold() not in ['tx', 'texas']:
        supported_state = False
        cost = -1
        distance = -1
    else:
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
        supported_state = True
    if not to_door:
        cost += 50

    return cost, distance, supported_state


def calculate_distance(from_address, to_address):
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    try:
        address1 = gmaps.geocode(address=from_address)
        address2 = gmaps.geocode(address=to_address)

        to_state = get_address_state(address2[0]['address_components'])
        from_state = get_address_state(address1[0]['address_components'])

        address1_place_id = 'place_id:' + address1[0]['place_id']
        address2_place_id = 'place_id:' + address2[0]['place_id']

        distance = gmaps.distance_matrix(address1_place_id, address2_place_id, mode='driving', units='imperial', )

        return distance['rows'][0]['elements'][0]['distance']['text'], to_state, from_state
    except Exception as e:
        raise e


def get_address_state(address_components):
    for component in address_components:
        if 'administrative_area_level_1' in component['types'][0]:
            return component['long_name']
    else:
        return 'no state'


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


def qr_grid(request):
    sellers = Seller.objects.all()

    return render(request, 'seller-qr-grid.html', {'sellers': sellers})