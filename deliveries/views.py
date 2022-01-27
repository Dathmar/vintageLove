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
from .models import Delivery
from .forms import DeliverySelectionForm, PickupSelectionForm, ShippingAssociateForm, DateDriverForm
from bespokeShipping.models import Shipping, ShippingStatus
import logging

logger = logging.getLogger('app_api')


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_assignments(request):
    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date=
                                         tz('UTC').localize(datetime.now().today())).order_by('sequence')
    return render(request, 'deliveries.html', {'deliveries': deliveries})


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

        logger.info(delivery_form.is_valid())
        logger.info(pickup_form.is_valid())
        if delivery_form.is_valid() and pickup_form.is_valid() and date_driver_form.is_valid():
            pickup_assignment = request.POST.getlist('deliveries')
            delivery_assignment = request.POST.getlist('pickups')
            pickup_assignment_ids = []
            delivery_assignment_ids = []
            for pa in pickup_assignment:
                pickup_assignment_ids.append(int(pa))
            for da in delivery_assignment:
                delivery_assignment_ids.append(int(da))

            request.session['pickup_assignment_ids'] = pickup_assignment_ids
            request.session['delivery_assignment_ids'] = delivery_assignment_ids
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
        pickup_assignments = request.session.get('pickup_assignment_ids')
        delivery_assignments = request.session.get('delivery_assignment_ids')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')
        existing_assignments = Delivery.objects.filter(user__username=assignment_driver, scheduled_date=assignment_date)

        total_len = 0
        if pickup_assignments:
            total_len += len(pickup_assignments)
        if delivery_assignments:
            total_len += len(delivery_assignments)
        if existing_assignments:
            total_len += len(existing_assignments)

        forms = formset_factory(ShippingAssociateForm, extra=total_len)
        formset = forms()
        pickup_assignments_result = Shipping.objects.filter(id__in=pickup_assignments)
        delivery_assignments_result = Shipping.objects.filter(id__in=delivery_assignments)

        formset_context = []
        for i, form in enumerate(formset):
            if i <= len(pickup_assignments_result) - 1:
                form.fields['shipping'].queryset = Shipping.objects.filter(id=pickup_assignments_result[i].id)
                formset_context.append([form, pickup_assignments_result[i], None, 'Pickup'])
            elif i <= len(pickup_assignments_result) + len(delivery_assignments_result) - 1:
                i_context = i - len(pickup_assignments_result)
                form.fields['shipping'].queryset = Shipping.objects.filter(id=delivery_assignments_result[i_context].id)
                formset_context.append([form, delivery_assignments_result[i_context], None, 'Delivery'])
            else:
                i_context = i - len(pickup_assignments_result) - len(delivery_assignments_result)
                form.fields['shipping'].queryset = Shipping.objects.filter(id=existing_assignments[i_context].shipping_id)
                if existing_assignments[i_context].pickup:
                    formset_context.append([form, existing_assignments[i_context].shipping, existing_assignments[i_context].sequence, 'Pickup'])
                else:
                    formset_context.append([form, existing_assignments[i_context].shipping, existing_assignments[i_context].sequence, 'Delivery'])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': total_len})

    def post(self, request, *args, **kwargs):
        pickup_assignments = request.session.get('pickup_assignment_ids')
        delivery_assignments = request.session.get('delivery_assignment_ids')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')
        existing_assignments = Delivery.objects.filter(user__username=assignment_driver, scheduled_date=assignment_date)

        total_len = 0
        if pickup_assignments:
            total_len += len(pickup_assignments)
        if delivery_assignments:
            total_len += len(delivery_assignments)
        if existing_assignments:
            total_len += len(existing_assignments)

        ShippingAssociateFormset = formset_factory(ShippingAssociateForm, extra=total_len)

        shipping_formset = ShippingAssociateFormset(request.POST)
        if shipping_formset.is_valid():
            for form in shipping_formset:
                shipping = form.cleaned_data['shipping']
                sequence = form.cleaned_data['sequence']
                user = User.objects.get(username=assignment_driver)

                is_assignment = existing_assignments.filter(user=user, shipping=shipping, scheduled_date=assignment_date)

                if is_assignment.exists():
                    delivery = is_assignment.first()
                    pickup = delivery.pickup
                    delivery.sequence = sequence
                    delivery.pickup = pickup
                    delivery.save()
                else:
                    pickup = True
                    if shipping.id in pickup_assignments:
                        if shipping.id in delivery_assignments:
                            if Delivery.objects.filter(user=user, scheduled_date=assignment_date,
                                                       pickup=True).exists():
                                pickup = False
                    else:
                        pickup = False

                    delivery = Delivery.objects.create(
                        user=user,
                        scheduled_date=assignment_date,
                        sequence=sequence,
                        shipping=Shipping.objects.get(pk=shipping.id),
                        pickup=pickup,
                        blocked=False
                    )
                    delivery.save()
            return redirect(reverse('deliveries:assignments-create'))

        pickup_assignments_result = Shipping.objects.filter(id__in=pickup_assignments)
        delivery_assignments_result = Shipping.objects.filter(id__in=delivery_assignments)

        formset_context = []
        for i, form in enumerate(shipping_formset):
            if i <= len(pickup_assignments_result) - 1:
                form.fields['shipping'].queryset = Shipping.objects.filter(id=pickup_assignments_result[i].id)
                formset_context.append([form, pickup_assignments_result[i], None, 'Pickup'])
            elif i <= len(pickup_assignments_result) + len(delivery_assignments_result) - 1:
                i_context = i - len(pickup_assignments_result)
                form.fields['shipping'].queryset = Shipping.objects.filter(id=delivery_assignments_result[i_context].id)
                formset_context.append([form, delivery_assignments_result[i_context], None, 'Delivery'])
            else:
                i_context = i - len(pickup_assignments_result) - len(delivery_assignments_result)
                form.fields['shipping'].queryset = Shipping.objects.filter(
                    id=existing_assignments[i_context].shipping_id)
                if existing_assignments[i_context].pickup:
                    formset_context.append(
                        [form, existing_assignments[i_context].shipping, existing_assignments[i_context].sequence,
                         'Pickup'])
                else:
                    formset_context.append(
                        [form, existing_assignments[i_context].shipping, existing_assignments[i_context].sequence,
                         'Delivery'])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': total_len})


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

