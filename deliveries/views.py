from django.shortcuts import render, redirect, reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.views import View
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse

from pytz import timezone as tz
from datetime import datetime
from .models import Delivery, EquipmentStatus, Equipment
from .forms import DeliverySelectionForm, PickupSelectionForm, ShippingAssociateForm, DateDriverForm, \
    EquipmentStatusForm
from bespokeShipping.models import Shipping, ShippingStatus
import logging

logger = logging.getLogger('app_api')


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_assignments(request):
    morning_status = EquipmentStatus.objects.filter(user=request.user, timeperiod='morning',
                                                    schedule_date=tz('UTC').localize(datetime.now().today()))

    if not morning_status:
        return redirect('deliveries:equipment-status', tod='morning')

    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date=
                                         tz('UTC').localize(datetime.now().today())).order_by('sequence')

    if deliveries.filter(Q(complete=True) | Q(blocked=True)).count() != deliveries.count():
        return render(request, 'deliveries.html', {'deliveries': deliveries})

    evening_status = EquipmentStatus.objects.filter(timeperiod='evening', user=request.user,
                                                    schedule_date=tz('UTC').localize(datetime.now().today()))
    if not evening_status:
        return redirect('deliveries:equipment-status', tod='evening')

    return render(request, 'deliveries.html', {'deliveries': deliveries})


class EquipmentStatusView(LoginRequiredMixin, View):
    equipment_status_form = EquipmentStatusForm
    template = 'equipment_status.html'

    def get(self, request, *args, **kwargs):
        tod = kwargs.get('tod').casefold()
        form = self.equipment_status_form()

        return render(request, self.template, {'form': form, 'tod': tod})

    def post(self, request, *args, **kwargs):
        tod = kwargs.get('tod').casefold()
        form = self.equipment_status_form(request.POST, request.FILES)

        if form.is_valid():
            equipment_status = form.save(commit=False)
            equipment_status.user = request.user
            equipment_status.timeperiod = tod
            equipment_status.schedule_date = tz('UTC').localize(datetime.now().today())
            equipment_status.save()

            return redirect('deliveries:my-assignments')

        return render(request, self.template, {'form': form, 'tod': tod})


class CreateAssignmentsView(LoginRequiredMixin, View):
    login_url = '/accounts/login/?next=/assignments/create/'
    selection_template = 'create_assignment.html'
    assignment_template = 'associate_assignment.html'
    pickup_template = 'pickup_table.html'
    delivery_template = 'delivery_table.html'
    delivery_form = DeliverySelectionForm
    pickup_form = PickupSelectionForm
    date_driver_form = DateDriverForm
    delivery_query_set = Shipping.objects.filter(
        Q(status__name__in=['Barn', 'Pickup Complete']) | Q(status__name='Order Received', must_go_to_barn=0)).exclude(
        id__in=Delivery.objects.filter(scheduled_date__gte=datetime.today(), blocked=False).values_list('shipping_id'))
    pickup_query_set = Shipping.objects.filter(
        status__name='Order Received').exclude(
        id__in=Delivery.objects.filter(scheduled_date__gte=datetime.today(), blocked=False).values_list('shipping_id'))

    def get_deliver_pickups(self, form_type='delivery'):
        if form_type == 'delivery':
            form = self.delivery_form()
            form.fields['deliveries'].queryset = self.delivery_query_set
            objs = self.delivery_query_set
            enum = form.fields['deliveries'].choices
        else:
            form = self.pickup_form()
            form.fields['pickups'].queryset = self.pickup_query_set
            objs = self.pickup_query_set
            enum = form.fields['pickups'].choices

        form_set = []
        for i, choice in enumerate(enum):
            form_set.append([choice, objs[i]])

        return form_set

    def get(self, request):
        delivery_formset = self.get_deliver_pickups('delivery')
        pickup_formset = self.get_deliver_pickups('pickup')
        date_driver_form = self.date_driver_form()

        return render(request, self.selection_template, {'deliveries': delivery_formset,
                                                         'pickups': pickup_formset,
                                                         'date_driver_form': date_driver_form})

    def post(self, request):
        delivery_form = self.delivery_form(request.POST)
        pickup_form = self.pickup_form(request.POST)
        date_driver_form = self.date_driver_form(request.POST)

        delivery_form.fields['deliveries'].queryset = self.delivery_query_set
        pickup_form.fields['pickups'].queryset = self.pickup_query_set

        if delivery_form.is_valid() and pickup_form.is_valid() and date_driver_form.is_valid():
            pickup_assignment = request.POST.getlist('deliveries')
            delivery_assignment = request.POST.getlist('pickups')
            assignments = []  # list of tuples (shipping, delivery, pickup, sequence)
            existing_assignments = Delivery.objects.filter(scheduled_date=request.POST['delivery_date'],
                                                           user__username=request.POST['driver'])

            for pa in pickup_assignment:
                assignments.append((pa, None, True, None))
            for da in delivery_assignment:
                assignments.append((da, None, False, None))
            for ea in existing_assignments:
                assignments.append((ea.shipping.id, ea.id, ea.pickup, ea.sequence))

            request.session['assignments'] = assignments
            request.session['assignment_date'] = request.POST['delivery_date']
            request.session['assignment_driver'] = request.POST['driver']
            return redirect(reverse('deliveries:assignments-associate'))

        delivery_formset = []
        delivery_objs = self.delivery_query_set
        for i, form in enumerate(delivery_form.fields['deliveries'].choices):
            delivery_formset.append([form, delivery_objs[i]])

        pickup_formset = []
        pickup_objs = self.pickup_query_set
        for i, form in enumerate(pickup_form.fields['pickups'].choices):
            pickup_formset.append([form, pickup_objs[i]])

        return render(request, self.selection_template, {'deliveries': delivery_formset,
                                                         'pickups': pickup_formset,
                                                         'date_driver_form': date_driver_form})


class AssociateAssignmentsView(LoginRequiredMixin, View):
    login_url = '/accounts/login/?next=/assignments/associate/'
    assignment_template = 'associate_assignment.html'
    form = ShippingAssociateForm

    def get(self, request, *args, **kwargs):
        assignments = request.session.get('assignments')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')

        forms = formset_factory(ShippingAssociateForm, extra=len(assignments))
        formset = forms()

        formset_context = []
        for i, form in enumerate(formset):
            # assignments is a list of tuples (shipping, delivery, pickup, sequence)
            assignments[i][0] = Shipping.objects.get(id=assignments[i][0])
            formset_context.append([form, assignments[i]])
        logger.info(assignments)
        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': len(assignments)})

    def post(self, request, *args, **kwargs):
        assignments = request.session.get('assignments')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')

        ShippingAssociateFormset = formset_factory(ShippingAssociateForm, extra=len(assignments))

        formset = ShippingAssociateFormset(request.POST)
        logger.info(formset.is_valid())
        if formset.is_valid():
            associated_shippings = []
            for i, form in enumerate(formset):
                sequence = form.cleaned_data['sequence']
                user = User.objects.get(username=assignment_driver)

                # assignments is a list of tuples (shipping, delivery, pickup, sequence)
                if assignments[i][1]:  # if a delivery exists then update the delivery
                    # delivery exists should update the existing delivery
                    delivery = Delivery.objects.get(id=assignments[i][1])
                    delivery.sequence = sequence
                    delivery.save()
                else:  # if a delivery does not exist then create a new delivery
                    delivery = Delivery.objects.create(
                        user=user,
                        scheduled_date=assignment_date,
                        sequence=sequence,
                        shipping=Shipping.objects.get(pk=assignments[i][0]),
                        pickup=assignments[i][2],
                        blocked=False
                    )
                    delivery.save()

                request.session['assignments'] = None
            return redirect(reverse('deliveries:assignments-create'))

        formset_context = []
        for i, form in enumerate(formset):
            # assignments is a list of tuples (shipping, delivery, pickup, sequence)
            assignments[i][0] = Shipping.objects.get(id=assignments[i][0])
            formset_context.append([form, assignments[i]])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': len(assignments)})


def block_assignment(request, delivery_id):
    try:
        delivery = Delivery.objects.get(pk=delivery_id)
        delivery.blocked = True
        delivery.save()
        return JsonResponse({'new_url': reverse('deliveries:unblock-assignment', kwargs={'delivery_id': delivery_id}),
                             'new_label': 'Unblock'}, status=200)
    except:
        return JsonResponse({'success': False}, status=400)


def unblock_assignment(request, delivery_id):
    try:
        delivery = Delivery.objects.get(pk=delivery_id)
        delivery.blocked = False
        delivery.save()
        return JsonResponse({'new_url': reverse('deliveries:block-assignment', kwargs={'delivery_id': delivery_id}),
                             'new_label': 'Block'}, status=200)
    except:
        return JsonResponse({'success': False}, status=400)


def complete_assignment(request, delivery_id):
    try:
        delivery = Delivery.objects.get(pk=delivery_id)
        shipping = delivery.shipping
        if shipping.status.name == 'Order Received':
            shipping.status = ShippingStatus.objects.get(name='Pickup Complete')
        else:
            shipping.status = ShippingStatus.objects.get(name='Delivery Complete')
        delivery.complete = True
        delivery.save()
        shipping.save()
        return JsonResponse({'success': True}, status=200)
    except:
        return JsonResponse({'success': False}, status=400)

