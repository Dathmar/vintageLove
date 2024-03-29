import json
import googlemaps
import uuid

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views import View
from django.contrib.auth.models import User

from .forms import SizeForm, ShipToForm, DeliveryLevel, FromForm, InsuranceForm, DeliveryLevelQuote, \
    InsuranceFormQuote, ShippingNotes, QuoteCostOverride
from .models import ShippingStatus, Quote, Shipping
from products.models import UserSeller, Seller
from orders.views import submit_payment
from deliveries.models import Delivery

from base.Emailing import send_quote_paid_notification


import logging
payments_logger = logging.getLogger('payments')
app_logger = logging.getLogger('app_api')



def quote_context(request):
    sellers = Seller.objects.all()
    return render(request, 'quote-context.html', {'sellers': sellers})


def shipping_detail(request, shipping_id):
    shipping = get_object_or_404(Shipping, id=shipping_id)
    drivers = User.objects.filter(groups__name='Driver').values_list('username', 'username')

    tods = Delivery.window_choices

    existing_pickup = Delivery.objects.filter(shipping=shipping, pickup=True).first()
    existing_delivery = Delivery.objects.filter(shipping=shipping, pickup=False).first()
    context = {
        'shipping': shipping,
        'drivers': drivers,
        'existing_pickup': existing_pickup,
        'existing_delivery': existing_delivery,
        'tods': tods,
    }
    return render(request, 'shipping-detail.html', context)


def is_valid_uuid(uuid_string, version=4):
    try:
        uuid.UUID(uuid_string, version=version)
    except ValueError:
        return False
    return True


class PayQuote(View):
    pay_template = 'quote-payment.html'
    complete_template = 'quote-payment-complete.html'

    def get(self, request, *args, **kwargs):
        encoding_id = kwargs.get('encoding')
        payments_logger.info(f'{encoding_id} PayQuote GET encoding_id: {encoding_id}')
        request.session['idempotency_shipping_key'] = str(uuid.uuid4())
        request.session['nonce'] = False

        if is_valid_uuid(encoding_id):
            quote = get_object_or_404(Quote, pk=encoding_id)
        else:
            quote = get_object_or_404(Quote, encoding=encoding_id)

        if quote.paid:
            payments_logger.info(f'{encoding_id} PayQuote quote already paid: {quote}')
            return render(request, self.complete_template, {'quote': quote})
        context = {
            'quote': quote,
            'hide_subscribe': True,
            'square_js_url': settings.SQUARE_JS_URL,
        }
        payments_logger.info(f'{encoding_id} PayQuote context: {context}')
        return render(request, 'quote-payment.html', context)

    def post(self, request, *args, **kwargs):
        encoding_id = kwargs.get('encoding')
        payments_logger.info(f'{encoding_id} PayQuote POST encoding_id: {encoding_id}')
        if is_valid_uuid(encoding_id):
            quote = get_object_or_404(Quote, pk=encoding_id)
        else:
            quote = get_object_or_404(Quote, encoding=encoding_id)

        payment_result = None
        if quote.paid:
            payments_logger.info(f'{encoding_id} PayQuote quote already paid: {quote}')
            return render(request, self.complete_template, {'quote': quote})

        if not quote.paid:
            payments_logger.info(f'{encoding_id} PayQuote quote not paid: {quote}')
            charge_cost = quote.cost * 100
            idempotency_key = request.session.get('idempotency_shipping_key')
            if not idempotency_key:
                idempotency_key = str(uuid.uuid4())
                request.session['idempotency_shipping_key'] = idempotency_key

            nonce = request.session.get('nonce')

            payments_logger.info(f'{encoding_id} PayQuote nonce: {nonce}')
            payments_logger.info(f'{encoding_id} PayQuote idempotency_key: {idempotency_key}')

            payment_result = submit_payment(charge_cost, nonce, idempotency_key)
            request.session['idempotency_shipping_key'] = False
            request.session['nonce'] = False

            payments_logger.info(f'{encoding_id} PayQuote payment_result: {str(payment_result)}')

            if payment_result == 'pass':
                quote.paid = True
                quote.save()
                payments_logger.info(f'{encoding_id} PayQuote marked quote paid: {quote}')
                send_quote_paid_notification(quote)
                init_status = ShippingStatus.objects.get(name='Order Received')
                if not quote.shipping:
                    shipping = Shipping.objects.create(
                        seller=quote.seller,
                        from_name=quote.from_name,
                        from_address=quote.from_address,
                        from_email=quote.from_email,
                        from_phone=quote.from_phone,

                        to_name=quote.to_name,
                        to_address=quote.to_address,
                        to_email=quote.to_email,
                        to_phone=quote.to_phone,

                        small_quantity=quote.small_quantity,
                        medium_quantity=quote.medium_quantity,
                        large_quantity=quote.large_quantity,
                        set_quantity=quote.set_quantity,

                        small_description=quote.small_description,
                        medium_description=quote.medium_description,
                        large_description=quote.large_description,
                        set_description=quote.set_description,
                        ship_location=quote.ship_location,

                        status=init_status,
                        notes=quote.notes,
                        pickup_requested_date=quote.pickup_requested_date,
                        delivery_requested_date=quote.delivery_requested_date,
                        must_go_to_barn=quote.must_go_to_barn,

                        insurance=quote.insurance,
                        cost=quote.cost,
                        distance=quote.distance
                    )
                    shipping.save()
                    quote.shipping = shipping
                    quote.save()

                return render(request, self.complete_template)

        context = {
            'quote': quote,
            'hide_subscribe': True,
            'square_js_url': settings.SQUARE_JS_URL,
        }

        if payment_result:
            payments_logger.info(f'{encoding_id} PayQuote payment errors: {str(payment_result)}')
            context |= {'payment_errors': payment_result}

        request.session['idempotency_shipping_key'] = str(uuid.uuid4())
        request.session['nonce'] = False
        return render(request, self.pay_template, context)


class CreateQuoteView(View):
    size_form = SizeForm
    ship_to_form = ShipToForm
    delivery_level = DeliveryLevelQuote
    insurance_form = InsuranceFormQuote
    from_form = FromForm
    shipping_notes = ShippingNotes
    quote_cost_override = QuoteCostOverride

    create_template = 'create-quote.html'
    complete_template = 'complete-quote.html'

    def get(self, request, seller_slug=None):
        size_form = self.size_form
        ship_to_form = self.ship_to_form
        delivery_level = self.delivery_level
        insurance_form = self.insurance_form
        shipping_notes = self.shipping_notes
        quote_cost_override = self.quote_cost_override

        seller = seller_context(request.user, seller_slug)

        if seller:
            from_form = None
        else:
            from_form = self.from_form

        context = {
            'size_form': size_form,
            'ship_to_form': ship_to_form,
            'delivery_level': delivery_level,
            'insurance_form': insurance_form,
            'from_form': from_form,
            'shipping_notes': shipping_notes,
            'quote_cost_override': quote_cost_override,
            'seller': seller,
            'hide_subscribe': True,
        }
        return render(request, self.create_template, context)

    def post(self, request, seller_slug=None):
        size_form = self.size_form(request.POST)
        ship_to_form = self.ship_to_form(request.POST)
        delivery_level = self.delivery_level(request.POST)
        insurance_form = self.insurance_form(request.POST)
        shipping_notes = self.shipping_notes(request.POST)
        quote_cost_override = self.quote_cost_override(request.POST)

        seller = seller_context(request.user, seller_slug)

        if seller:
            from_form = None
        else:
            from_form = self.from_form(request.POST)

        if size_form.is_valid() and ship_to_form.is_valid() and delivery_level.is_valid() and \
           insurance_form.is_valid() and (seller or from_form.is_valid()) and shipping_notes.is_valid():

            if seller:
                from_address = seller.street + '\n' + seller.city + ', ' + seller.state + ' ' + seller.zip
                from_name = seller.name
                from_email = seller.email
                from_phone = seller.phone
            else:
                from_name = from_form.cleaned_data['store_name']
                from_phone = from_form.cleaned_data['store_phone']
                from_email = from_form.cleaned_data['store_email']

                from_address = from_form.cleaned_data['store_address_1']
                if from_form.cleaned_data['store_address_2']:
                    from_address += '\n' + from_form.cleaned_data['store_address_2']
                from_address += '\n' + from_form.cleaned_data['store_city'] + ', ' \
                                + from_form.cleaned_data['store_state'] + ' ' \
                                + from_form.cleaned_data['store_postal_code']

            small_quantity = size_form.cleaned_data['size_small']
            medium_quantity = size_form.cleaned_data['size_medium']
            large_quantity = size_form.cleaned_data['size_large']
            set_quantity = size_form.cleaned_data['size_set']

            small_description = size_form.cleaned_data['small_description']
            medium_description = size_form.cleaned_data['medium_description']
            large_description = size_form.cleaned_data['large_description']
            set_description = size_form.cleaned_data['set_description']

            ship_sizes = {
                'small': small_quantity,
                'medium': medium_quantity,
                'large': large_quantity,
                'set': set_quantity
            }

            ship_to_first_name = ship_to_form.cleaned_data['first_name']
            ship_to_last_name = ship_to_form.cleaned_data['last_name']
            ship_to_address1 = ship_to_form.cleaned_data['address1']
            ship_to_address2 = ship_to_form.cleaned_data['address2']
            ship_to_city = ship_to_form.cleaned_data['city']
            ship_to_state = ship_to_form.cleaned_data['state']
            ship_to_postal_code = ship_to_form.cleaned_data['postal_code']
            ship_to_email = ship_to_form.cleaned_data['email']
            ship_to_phone = ship_to_form.cleaned_data['phone']

            ship_to_address = ship_to_address1
            if ship_to_address2:
                ship_to_address += '\n' + ship_to_address2
            ship_to_address += '\n' + ship_to_city + ', ' + ship_to_state + ' ' + ship_to_postal_code

            shipping_level = delivery_level.cleaned_data['level']
            insurance_level = insurance_form.cleaned_data['insure_level']

            cost, distance, supported_state = calculate_shipping_cost(
                    ship_sizes, from_address, ship_to_address, shipping_level, insurance_level)

            if quote_cost_override.is_valid():
                override_cost = quote_cost_override.cleaned_data['override_cost']

            if override_cost:
                cost = override_cost

            note = shipping_notes.cleaned_data['notes']
            delivery_requested_date = shipping_notes.cleaned_data['delivery_requested_date']
            pickup_requested_date = shipping_notes.cleaned_data['pickup_requested_date']
            must_go_to_barn = shipping_notes.cleaned_data['must_go_to_barn']

            quote = Quote.objects.create(
                seller=seller,
                from_name=from_name,
                from_address=from_address,
                from_email=from_email,
                from_phone=from_phone,

                to_name=ship_to_first_name + ' ' + ship_to_last_name,
                to_address=ship_to_address,
                to_email=ship_to_email,
                to_phone=ship_to_phone,

                small_quantity=small_quantity,
                medium_quantity=medium_quantity,
                large_quantity=large_quantity,
                set_quantity=set_quantity,

                small_description=small_description,
                medium_description=medium_description,
                large_description=large_description,
                set_description=set_description,
                ship_location=shipping_level,

                insurance=insurance_level,
                cost=cost,
                distance=distance,
                notes=note,
                delivery_requested_date=delivery_requested_date,
                pickup_requested_date=pickup_requested_date,
                must_go_to_barn=must_go_to_barn,

                paid=False,
            )
            quote.save()
            change_url = f'/admin/bespokeShipping/quote/{quote.id}/change/'
            return render(request, 'complete-quote.html',
                          {
                              'quote': quote,
                              'change_url': change_url,
                          })

        else:
            context = {
                'size_form': size_form,
                'ship_to_form': ship_to_form,
                'delivery_level': delivery_level,
                'insurance_form': insurance_form,
                'from_form': from_form,
                'shipping_notes': shipping_notes,
                'quote_cost_override': quote_cost_override,
                'seller': seller,
                'hide_subscribe': True,
            }
            return render(request, self.create_template, context)


def seller_context(user, seller_slug=None):
    if seller_slug.casefold() == 'unknown' or not seller_slug:
        return None
    elif seller_slug:
        return get_object_or_404(Seller, slug=seller_slug)
    elif user.is_authenticated:
        return get_object_or_404(UserSeller, user=user).seller
    else:
        return None


class CreateView(View):
    size_form = SizeForm
    ship_to_form = ShipToForm
    delivery_level = DeliveryLevel
    insurance_form = InsuranceForm
    from_form = FromForm

    create_template = 'bespoke_shipping.html'
    complete_template = 'bespoke_shipping_complete.html'

    def get(self, request, *args, **kwargs):
        request.session['idempotency_shipping_key'] = str(uuid.uuid4())

        seller = seller_context(request.user, kwargs.get('seller_slug'))
        if seller:
            from_form = self.from_form
        else:
            from_form = None

        context = {
            'size_form': self.size_form,
            'ship_to_form': self.ship_to_form,
            'delivery_level': self.delivery_level,
            'insurance_form': self.insurance_form,
            'seller': seller,
            'hide_subscribe': True,
            'square_js_url': settings.SQUARE_JS_URL,
        }

        if from_form:
            context.update({'from_form': from_form})

        return render(request, self.create_template, context)

    def post(self, request, *args, **kwargs):
        size_form = self.size_form(request.POST)
        ship_to_form = self.ship_to_form(request.POST)
        delivery_level = self.delivery_level(request.POST)
        insurance_form = self.insurance_form(request.POST)

        seller = seller_context(request, kwargs.get('seller_slug'))
        if seller:
            from_form = None
        else:
            from_form = self.from_form(request.POST)

        # if all forms are valid
        if size_form.is_valid() and ship_to_form.is_valid() and delivery_level.is_valid() and \
           insurance_form.is_valid() and (seller or from_form.is_valid()):
            pass

        else:  # if any form is invalid
            context = {
                'size_form': size_form,
                'ship_to_form': ship_to_form,
                'delivery_level': delivery_level,
                'insurance_form': insurance_form,
                'seller': seller,
                'hide_subscribe': True,
                'square_js_url': settings.SQUARE_JS_URL,
            }

            if from_form:
                context.update({'from_form': from_form})

            return render(request, self.create_template, context)


def create(request, seller_slug=None):
    from_form = None

    request.session['idempotency_shipping_key'] = str(uuid.uuid4())

    if request.method == 'POST':
        size_form = SizeForm(request.POST)
        ship_to_form = ShipToForm(request.POST)
        delivery_level = DeliveryLevel(request.POST)
        insurance_form = InsuranceForm(request.POST)

        seller = None
        from_form_valid = True
        if seller_slug and seller_slug.casefold() != 'unknown':
            seller = get_object_or_404(Seller, slug=seller_slug)
        elif seller_slug == 'unknown' or request.user.is_anonymous:

            from_form = FromForm(request.POST)
            if from_form.is_valid():
                from_name = from_form.cleaned_data['store_name']
                from_phone = from_form.cleaned_data['store_phone']
                from_email = from_form.cleaned_data['store_email']

                from_address = from_form.cleaned_data['store_address_1']
                if from_form.cleaned_data['store_address_2']:
                    from_address += '\n' + from_form.cleaned_data['store_address_2']
                from_address += '\n' + from_form.cleaned_data['store_city'] + ', ' \
                                + from_form.cleaned_data['store_state'] + ' ' \
                                + from_form.cleaned_data['store_postal_code']
            else:
                from_form_valid = False
        else:
            seller = get_object_or_404(UserSeller, user=request.user).seller

        if seller:
            from_address = seller.street + '\n' + seller.city + ', ' + seller.state + ' ' + seller.zip
            from_name = seller.name
            from_email = seller.email
            from_phone = seller.phone

        if size_form.is_valid() and ship_to_form.is_valid() and delivery_level.is_valid() \
                and from_form_valid and insurance_form.is_valid():

            small_quantity = size_form.cleaned_data['size_small']
            medium_quantity = size_form.cleaned_data['size_medium']
            large_quantity = size_form.cleaned_data['size_large']
            set_quantity = size_form.cleaned_data['size_set']

            small_description = size_form.cleaned_data['small_description']
            medium_description = size_form.cleaned_data['medium_description']
            large_description = size_form.cleaned_data['large_description']
            set_description = size_form.cleaned_data['set_description']

            ship_sizes = {
                'small': small_quantity,
                'medium': medium_quantity,
                'large': large_quantity,
                'set': set_quantity
            }

            ship_to_first_name = ship_to_form.cleaned_data['first_name']
            ship_to_last_name = ship_to_form.cleaned_data['last_name']
            ship_to_address1 = ship_to_form.cleaned_data['address1']
            ship_to_address2 = ship_to_form.cleaned_data['address2']
            ship_to_city = ship_to_form.cleaned_data['city']
            ship_to_state = ship_to_form.cleaned_data['state']
            ship_to_postal_code = ship_to_form.cleaned_data['postal_code']
            ship_to_email = ship_to_form.cleaned_data['email']
            ship_to_phone = ship_to_form.cleaned_data['phone']

            ship_to_address = ship_to_address1
            if ship_to_address2:
                ship_to_address += '\n' + ship_to_address2
            ship_to_address += '\n' + ship_to_city + ', ' + ship_to_state + ' ' + ship_to_postal_code

            shipping_level = delivery_level.cleaned_data['level']
            insurance_level = insurance_form.cleaned_data['insure_level']

            cost, distance, supported_state = calculate_shipping_cost(ship_sizes, from_address,
                                                                      ship_to_address, shipping_level, insurance_level)

            if '123 test ln' in ship_to_address.casefold():
                cost = 0.01
                distance = 0
                supported_state = True

            # now charge the card
            charge_cost = cost * 100
            idempotency_key = request.session.get('idempotency_shipping_key')
            nonce = request.session.get('nonce')

            payment_result = submit_payment(charge_cost, nonce, idempotency_key)
            request.session['idempotency_shipping_key'] = False

            if payment_result == 'pass':
                # now create the shipping
                init_status = ShippingStatus.objects.get(name='Order Received')
                shipping = Shipping.objects.create(
                    seller=seller,
                    from_name=from_name,
                    from_address=from_address,
                    from_email=from_email,
                    from_phone=from_phone,

                    to_name=ship_to_first_name + ' ' + ship_to_last_name,
                    to_address=ship_to_address,
                    to_email=ship_to_email,
                    to_phone=ship_to_phone,

                    small_quantity=small_quantity,
                    medium_quantity=medium_quantity,
                    large_quantity=large_quantity,
                    set_quantity=set_quantity,

                    small_description=small_description,
                    medium_description=medium_description,
                    large_description=large_description,
                    set_description=set_description,
                    ship_location=shipping_level,

                    status=init_status,

                    insurance=insurance_level,
                    cost=cost,
                    distance=distance)
                shipping.save()

                return render(request, 'bespoke_shipping_complete.html', {'shipping': shipping})
            else:

                app_logger.error(f'Payment failed for shipping: {str(payment_result)} - {ship_to_first_name} {ship_to_last_name} - {ship_to_phone} - {ship_to_email}')
                context = {
                    'size_form_errors': size_form.errors,
                    'size_form': size_form,
                    'ship_to_form': ship_to_form,
                    'delivery_level': delivery_level,
                    'delivery_level_errors': delivery_level.errors,
                    'insurance_form': insurance_form,
                    'insurance_form_errors': insurance_form.errors,
                    'seller': seller,
                    'hide_subscribe': True,
                    'square_js_url': settings.SQUARE_JS_URL,
                    'payment_errors': payment_result
                }

                if from_form:
                    context.update({'from_form': from_form})
                return render(request, 'bespoke_shipping.html', context)
        else:
            ship_to_first_name = ship_to_form.cleaned_data['first_name']
            ship_to_last_name = ship_to_form.cleaned_data['last_name']
            ship_to_email = ship_to_form.cleaned_data['email']
            ship_to_phone = ship_to_form.cleaned_data['phone']

            if size_form.errors:
                app_logger.error(f'Size form errors: {str(size_form.errors)} - {ship_to_first_name} {ship_to_last_name} '
                             f'- {ship_to_phone} - {ship_to_email}')
            if ship_to_form.errors:
                app_logger.error(f'Ship to form errors: {str(ship_to_form.errors)} - {ship_to_first_name} '
                             f'{ship_to_last_name} - {ship_to_phone} - {ship_to_email}')
            if delivery_level.errors:
                app_logger.error(f'Delivery level errors: {str(delivery_level.errors)} - '
                             f'{ship_to_first_name} {ship_to_last_name} - {ship_to_phone} - {ship_to_email}')
            if insurance_form.errors:
                app_logger.error(f'Insurance form errors: {str(insurance_form.errors)} - '
                             f'{ship_to_first_name} {ship_to_last_name} - {ship_to_phone} - {ship_to_email}')

            context = {
                'size_form': size_form,
                'ship_to_form': ship_to_form,
                'delivery_level': delivery_level,
                'insurance_form': insurance_form,
                'seller': seller,
                'hide_subscribe': True,
                'square_js_url': settings.SQUARE_JS_URL,
            }

            if from_form:
                context.update({'from_form': from_form})
            return render(request, 'bespoke_shipping.html', context)
    from_form = None
    if seller_slug and seller_slug.casefold() != 'unknown':
        seller = get_object_or_404(Seller, slug=seller_slug)
    elif seller_slug == 'unknown' or request.user.is_anonymous:
        from_form = FromForm()
        seller = None
    else:
        seller = get_object_or_404(UserSeller, user=request.user).seller

    size_form = SizeForm()
    ship_to_form = ShipToForm()
    delivery_level = DeliveryLevel()
    insurance_form = InsuranceForm()
    context = {
        'size_form': size_form,
        'ship_to_form': ship_to_form,
        'delivery_level': delivery_level,
        'insurance_form': insurance_form,
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
        ship_sizes = body['ship_sizes']
        from_address = body['from_address']
        to_address = body['to_address']
        to_door = body['to_door']
        insurance = body['insurance']

        try:
            cost, distance, supported_state = calculate_shipping_cost(ship_sizes, from_address, to_address, to_door,
                                                                      insurance)
            if '123 test ln' in to_address.casefold():
                cost = 0.01
                distance = 0
                supported_state = True

            return JsonResponse({'cost': cost, 'distance': str(distance), 'supported_state': supported_state})
        except Exception as e:
            return JsonResponse({'error': str(e)})

    return HttpResponseNotAllowed(['POST', ])


def calculate_shipping_cost(ship_sizes, from_address, to_address, to_door, insurance):
    distance, to_state, from_state = calculate_distance(from_address, to_address)
    distance = float(distance.split(' ')[0].replace(',', ''))
    cost = 0

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
                '0-50': 75,
                '51-100': 100,
                '101-150': 150,
                '151-200': 150,
                '201-250': 200,
                '251': 200
            },
            'medium': {
                '0-50': 150,
                '51-100': 150,
                '101-150': 200,
                '151-200': 200,
                '201-250': 300,
                '251': 300
            },
            'large': {
                '0-50': 200,
                '51-100': 250,
                '101-150': 300,
                '151-200': 300,
                '201-250': 500,
                '251': 500
            },
            'set': {
                '0-50': 300,
                '51-100': 350,
                '101-150': 400,
                '151-200': 500,
                '201-250': 700,
                '251': 750
            },
        }

        current_item = 0

        for size, quantity in ship_sizes.items():
            size_cost = shipping_chart[size][distance_range]

            for i in range(int(quantity)):
                current_item += 1
                if current_item == 1:
                    discount = 1
                elif current_item == 2:
                    discount = 0.7
                elif current_item in (3, 4, 5):
                    discount = 0.5
                else:
                    discount = 0.25

                cost += size_cost * discount

        supported_state = True

    if cost > 1900:
        cost = 1900

    if to_door == 'placement':
        cost += 50

    if type(insurance) == str and insurance == 'False':
        insurance = False

    if insurance:
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
        app_logger.error(f'error during distance calculation {e}')
        raise e


def get_address_state(address_components):
    for component in address_components:
        if 'administrative_area_level_1' in component['types'][0]:
            return component['long_name']
    else:
        return 'no state'


def qr_grid(request):
    sellers = Seller.objects.all()

    return render(request, 'seller-qr-grid.html', {'sellers': sellers})

