from django.shortcuts import render, redirect, reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.views import View
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from pytz import timezone as tz
from datetime import datetime
from .models import Delivery
from .forms import DeliverySelectionForm, PickupSelectionForm, ShippingAssociateForm, DateDriverForm
from bespokeShipping.models import Shipping
import logging

logger = logging.getLogger('app_api')


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_assignments(request):
    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date=
                                         tz('UTC').localize(datetime.now().today()))
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
        id__in=Delivery.objects.filter(scheduled_date__gte=datetime.today()).values_list('shipping_id'))
    pickup_query_set = Shipping.objects.filter(
        status__name='Order Received').exclude(
        id__in=Delivery.objects.filter(scheduled_date__gte=datetime.today()).values_list('shipping_id'))

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
        total_len = 0
        if pickup_assignments:
            total_len += len(pickup_assignments)
        if delivery_assignments:
            total_len += len(delivery_assignments)
        forms = formset_factory(ShippingAssociateForm, extra=total_len)
        formset = forms()
        pickup_assignments_result = Shipping.objects.filter(id__in=pickup_assignments)
        delivery_assignments_result = Shipping.objects.filter(id__in=delivery_assignments)

        formset_context = []
        for i, form in enumerate(formset):
            if i <= len(pickup_assignments_result) - 1:
                form.fields['shipping'].queryset = Shipping.objects.filter(id=pickup_assignments_result[i].id)
                formset_context.append([form, pickup_assignments_result[i], 'Pickup'])
            else:
                form.fields['shipping'].queryset = Shipping.objects.filter(id=delivery_assignments_result[i - len(pickup_assignments_result)].id)
                formset_context.append([form, delivery_assignments_result[i - len(pickup_assignments_result)], 'Delivery'])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': total_len})

    def post(self, request, *args, **kwargs):
        pickup_assignments = request.session.get('pickup_assignment_ids')
        delivery_assignments = request.session.get('delivery_assignment_ids')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')
        total_len = 0
        if pickup_assignments:
            total_len += len(pickup_assignments)
        if delivery_assignments:
            total_len += len(delivery_assignments)

        ShippingAssociateFormset = formset_factory(ShippingAssociateForm, extra=total_len)

        shipping_formset = ShippingAssociateFormset(request.POST)
        if shipping_formset.is_valid():
            for form in shipping_formset:
                shipping = form.cleaned_data['shipping']
                sequence = form.cleaned_data['sequence']
                delivery = Delivery.objects.create(
                    user=User.objects.get(username=assignment_driver),
                    scheduled_date=assignment_date,
                    sequence=sequence,
                    shipping=Shipping.objects.get(pk=shipping.id)
                )
                delivery.save()
            return redirect(reverse('deliveries:assignments-create'))

        pickup_assignments_result = Shipping.objects.filter(id__in=pickup_assignments)
        delivery_assignments_result = Shipping.objects.filter(id__in=delivery_assignments)

        formset_context = []
        for i, form in enumerate(shipping_formset):
            if i <= len(pickup_assignments_result) - 1:
                form.fields['shipping'].queryset = Shipping.objects.filter(id=pickup_assignments_result[i].id)
                formset_context.append([form, pickup_assignments_result[i], 'Pickup'])
            else:
                form.fields['shipping'].queryset = Shipping.objects.filter(
                    id=delivery_assignments_result[i - len(pickup_assignments_result)].id)
                formset_context.append(
                    [form, delivery_assignments_result[i - len(pickup_assignments_result)], 'Delivery'])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': total_len})
