from django.shortcuts import render
from django.conf import settings
from django.forms.formsets import formset_factory
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST

from .forms import DesignerForm, ItemForm, ToAddressForm, OverrideForm
from products.models import Seller
from designers.models import Designer
from items.models import Item
from deliveries.models import PdService
from repairs.models import Repair
from storage.models import Storage
from receiving.models import Receiving
from assembly.models import Assembly

from .models import ServiceAreas, Quote, QuoteItem

import googlemaps

import logging
logger = logging.getLogger('app_api')


# Create your views here.
def create_quote(request):
    google_api_key = settings.GOOGLE_PLACES_API_KEY
    empty_item_formset = formset_factory(ItemForm, extra=1)
    empty_item_forms = empty_item_formset()
    empty_form = render_to_string('quotes/item-form.html', {'item_form': empty_item_forms[0]})
    empty_form = empty_form.replace('form-0', 'form-__prefix__')

    if request.method == 'POST':
        submit_result = submit_quote(request)

        if submit_result:
            context = {
                'quote': submit_result,
            }

            return render(request, 'quotes/completed-quote-form.html', context)
        else:
            designers = DesignerForm(request.POST)
            ItemFormSet = formset_factory(ItemForm)
            item_forms = ItemFormSet(request.POST)
            to_address = ToAddressForm(request.POST)

            context = {
                'designers': designers,
                'item_forms': item_forms,
                'to_address': to_address,
                'google_api_key': google_api_key,
                'empty_form': empty_form,
            }
            return render(request, 'quotes/create-quote.html', context)

    else:
        designers = DesignerForm()
        ItemFormSet = formset_factory(ItemForm, extra=2)
        item_forms = ItemFormSet()
        to_address = ToAddressForm()
        context = {
            'designers': designers,
            'item_forms': item_forms,
            'to_address': to_address,
            'google_api_key': google_api_key,
            'empty_form': empty_form,
        }
        return render(request, 'quotes/create-quote.html', context)


def build_item_quote(request):
    """
        function takes a request of an item formset and returns a json response with a list of items and their prices
        are listed as a due now and monthly payment for services.

        returns: items_quote = [{'index': 1,
                                 'locality': 'San Antonio',
                                 'services': [{'name': 'pickup', 'due_now': '99.00', 'hourly':  '0.00', 'daily': '0.00'},
                                              {'name': 'delivery', 'due_now': '99.00', 'hourly':  '0.00', 'daily': '0.00'}],
                                 'totals': {'due_now': '198.00', 'hourly': '0.00', 'daily': '0.00'}},

        Prices:
            Receiving: $29.00 per item.


            Assembly: $69.00 per hour
            In-home Assembly: 199.00 per hour
            Repair: $99.00 per hour + cost of materials
            Storage: $1 a day per storage unit (7ft x 7ft x 7ft)
            Pickup and/or Delivery:
                Local:   $99.00 first item
                        +$30 each additional medium-large item
                        +$15 each additional small item
                Intra-city:  $199.00 first item
                            +$50 each additional medium-large item
                            +$25 each additional small item
                Other: $999.00 all items
        """

    ItemFormSet = formset_factory(ItemForm)
    item_forms = ItemFormSet(request.POST)

    to_address_form = ToAddressForm(request.POST)

    if to_address_form.is_valid():
        to_address_clean = to_address_form.cleaned_data
        to_address = to_address_clean.get('to_address')
    else:
        return JsonResponse({'error': 'to address form is not valid'}, status=203)

    repair_cost = 99.00
    storage_cost = 1.00

    shipping_cost = {
        'local': {
            'first': {
                'sm': 99,
                'md': 99,
                'lg': 99,
                'xl': 9999
            },
            'additional': {
                'sm': 15,
                'md': 30,
                'lg': 30,
                'xl': 9999
            }
        },
        'intra-city': {
            'first': {
                'sm': 199,
                'md': 199,
                'lg': 199,
                'xl': 9999
            },
            'additional': {
                'sm': 25,
                'md': 50,
                'lg': 50,
                'xl': 9999
            }
        },
    }

    items_quote = []
    order_localities = []

    logger.info(f'Fetching a new quote for {request.user}')

    quote_totals = {'due_now': 0, 'hourly': 0, 'daily': 0}

    for i, item_form in enumerate(item_forms):
        services = []
        item_totals = {'due_now': 0, 'hourly': 0, 'daily': 0}
        if item_form.is_valid():
            logger.info(f'form {i} is valid')
            clean = item_form.cleaned_data
            if clean.get('custom_from_address'):
                from_address = clean.get('from_address')
            else:
                seller = Seller.objects.get(id=clean.get('from_seller'))
                from_address = f'{seller.street}, {seller.city}, {seller.state} {seller.zip}'

            logger.info(f'getting locality for form {i}')

            item_is_local, matched_localities = is_local(from_address, to_address)
            logger.info(f'localities is {matched_localities}')

            # add in cross local to aggregate quotes with local and inta-city items
            item_size = clean.get('size')
            hourly = 0
            daily = 0
            due_now = 0

            first_item = is_first(order_localities, matched_localities)
            quantity = clean.get('quantity')

            if item_is_local:
                if not first_item:
                    due_now = shipping_cost['local']['additional'][item_size]
                else:
                    due_now = shipping_cost['local']['first'][item_size]

                due_now += shipping_cost['local']['additional'][item_size] * (quantity - 1)
            else:
                if not first_item:
                    due_now = shipping_cost['intra-city']['additional'][item_size]
                else:
                    due_now = shipping_cost['intra-city']['first'][item_size]

                due_now += shipping_cost['local']['additional'][item_size] * (quantity - 1)

            if clean.get('delivery') and clean.get('pickup'):
                services.append({'name': 'pickup', 'due_now': due_now/2, 'hourly': '0.00', 'daily': '0.00'})
                services.append({'name': 'delivery', 'due_now': due_now/2, 'hourly': '0.00', 'daily': '0.00'})
            elif clean.get('delivery'):
                services.append({'name': 'delivery', 'due_now': due_now, 'hourly': '0.00', 'daily': '0.00'})
            elif clean.get('pickup'):
                services.append({'name': 'pickup', 'due_now': due_now, 'hourly': '0.00', 'daily': '0.00'})

            if clean.get('repair'):
                hourly += repair_cost
                services.append({'name': 'repair', 'due_now': '0.00', 'hourly': repair_cost, 'daily': '0.00'})

            if clean.get('storage'):
                daily += storage_cost
                services.append({'name': 'storage', 'due_now': '0.00', 'hourly': '0.00', 'daily': storage_cost})

            if clean.get('insured'):
                due_now += 50.00
                services.append({'name': 'storage', 'due_now': due_now, 'hourly': '0.00', 'daily': '0.00'})

            item_totals['due_now'] += due_now
            item_totals['hourly'] += hourly
            item_totals['daily'] += daily
            order_localities.append(matched_localities)

            quote_totals['due_now'] += due_now
            quote_totals['hourly'] += hourly
            quote_totals['daily'] += daily

            item_quote = {
                'index': i,
                'locality': matched_localities,
                'services': services,
                'totals': item_totals,
            }

            items_quote.append(item_quote)
        else:
            return {"error": f'form {i} is incomplete', 'success': False}

    return {"items_quote": items_quote, 'order_total': quote_totals, "success": True}


def is_first(order_localities, matched_localities):
    if not order_localities:
        return True

    for locality in order_localities:
        if locality in matched_localities:
            return False

    return True


@require_POST
def fetch_quote(request):
    item_quote = build_item_quote(request)

    if not item_quote['success']:
        return JsonResponse(item_quote, status=204)
    else:
        quote_summary_table = build_summary_table(item_quote)
        return JsonResponse({'html': quote_summary_table, 'success': True}, status=200)


def build_summary_table(items_quote):
    override_form = OverrideForm(initial={'override_due_now': items_quote['order_total']['due_now']})
    items_quote.update({'override_form': override_form})
    t = render_to_string('quotes/quote-summary.html', context=items_quote)
    return t


@require_POST
def submit_quote(request):
    designers = DesignerForm(request.POST)
    ItemFormSet = formset_factory(ItemForm)
    item_forms = ItemFormSet(request.POST)
    to_address_form = ToAddressForm(request.POST)
    override_form = OverrideForm(request.POST)

    if override_form.is_valid():
        or_clean = override_form.cleaned_data
        due_now = or_clean['override_due_now']
    else:
        return None

    designer_obj = None
    designer_pays = None

    if designers.is_valid():
        designers_clean = designers.cleaned_data
        allow_designer = designers_clean.get('allow_designer')
        if allow_designer:
            designer_pays = designers_clean.get('designer_pays')
            designer_name = designers_clean.get('designer_name')
            designer_obj = Designer.objects.get(id=designer_name)
    else:
        return None

    if to_address_form.is_valid():
        to_address_form_clean = to_address_form.cleaned_data
        to_name = to_address_form_clean.get('to_name')
        to_address = to_address_form_clean.get('to_address')
        to_phone = to_address_form_clean.get('to_phone')
        to_email = to_address_form_clean.get('to_email')
        delivery_notes = to_address_form_clean.get('delivery_notes')
    else:
        return None

    if item_forms.is_valid():
        if designer_pays:
            quote = Quote.objects.create(
                designer=designer_obj,
                to_name=to_name,
                to_email=to_email,
                to_address=to_address,
                to_phone=to_phone,
                due_now=due_now,
            )
            quote.save()
        else:
            quote = Quote.objects.create(
                to_name=to_name,
                to_email=to_email,
                to_address=to_address,
                to_phone=to_phone,
                due_now=due_now,
            )
            quote.save()

        for item_form in item_forms:
            item_form_clean = item_form.cleaned_data
            pickup = item_form_clean.get('pickup')
            delivery = item_form_clean.get('delivery')
            receiving = item_form_clean.get('receiving')
            storage = item_form_clean.get('storage')
            repair = item_form_clean.get('repair')
            assembly = item_form_clean.get('assembly')
            insured = item_form_clean.get('insured')
            size = item_form_clean.get('size')
            quantity = item_form_clean.get('quantity')
            notes = item_form_clean.get('notes')
            description = item_form_clean.get('description')

            if item_form_clean.get('custom_from_address'):
                from_address = item_form_clean.get('from_address')
            else:
                seller = Seller.objects.get(id=item_form_clean.get('from_seller'))
                from_address = f'{seller.street}, {seller.city}, {seller.state} {seller.zip}'

            pickup_date = item_form_clean.get('pickup_date')
            delivery_date = item_form_clean.get('delivery_date')

            item = Item.objects.create(
                size=size,
                quantity=quantity,
                description=description,
                notes=notes,
                insured=insured,
            )
            item.save()

            quote_item = QuoteItem.objects.create(
                quote=quote,
                item=item
            )
            quote_item.save()

            if pickup:
                pickup_service = PdService.objects.create(
                    item=item,
                    pickup=True,
                    desired_date=pickup_date,
                    address=from_address,
                )
                pickup_service.save()

            if delivery:
                delivery_service = PdService.objects.create(
                    item=item,
                    pickup=True,
                    desired_date=delivery_date,
                    address=to_address,
                    delivery_notes=delivery_notes
                )
                delivery_service.save()

            if repair:
                repair_service = Repair.objects.create(
                    item=item,
                )
                repair_service.save()

            if storage:
                storage_service = Storage.objects.create(
                    item=item,
                )
                storage_service.save()

            if assembly:
                assembly_service = Assembly.objects.create(
                    item=item,
                )
                assembly_service.save()

            if receiving:
                receiving_service = Receiving.objects.create(
                    item=item,
                )
                receiving_service.save()

        return quote
    else:
        return None


def is_local(from_address, to_address):
    # add stuff for service teams.
    try:
        # get the to and from cities from the addresses
        to_city = get_address_city(to_address)
        from_city = get_address_city(from_address)

        # get the service areas that serve the cities
        logger.info(f'Finding localities | to - {to_city} | from - {from_city}')
        to_service_areas = ServiceAreas.objects.filter(locality=to_city)
        from_service_areas = ServiceAreas.objects.filter(locality=from_city)

        # if the cities share a service area then they are local
        to_localities = list(to_service_areas.values_list('locality', flat=True))
        matched_localities = list(from_service_areas.filter(
            locality__in=to_localities).values_list('locality', flat=True))

        if len(matched_localities) > 0:
            logger.info(f'The delivery is local | to_localities - {to_localities} | '
                        f'matched_localities - {matched_localities}')
            return True, matched_localities

        logger.info(f'Not local')
        return False, None
    except Exception as e:
        logger.error(f'error during local calculation')
        logger.error(e)
        raise e


def get_address_city(address):
    logger.info(f'getting city from address {address}')
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    # detect if the address is a Google Maps address or normal address.
    if "{" not in str(address):
        geo_address = gmaps.geocode(address)
    else:
        geo_address = address

    try:
        for component in geo_address[0]['address_components']:
            if 'locality' in component['types'][0]:
                return component['long_name']
        else:
            return 'no city'
    except Exception as e:
        logger.error(f'error during get_address_city {address}')
        logger.error(e)
        raise e


