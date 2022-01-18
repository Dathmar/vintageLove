from django.shortcuts import render, redirect, reverse
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from pytz import timezone as tz
from datetime import datetime
from .models import Delivery
from .forms import ShippingSelectionForm, ShippingAssociateForm, DateDriverForm
from bespokeShipping.models import Shipping
import logging

logger = logging.getLogger('app_api')


# Create your views here.
@login_required(login_url='/accounts/login/?next=/deliveries/')
def my_assignments(request):
    deliveries = Delivery.objects.filter(user=request.user,
                                         scheduled_date__gte=
                                         tz('UTC').localize(datetime.now().today()))
    return render(request, 'deliveries.html', {'deliveries': deliveries})


class CreateAssignmentsView(LoginRequiredMixin, View):
    login_url = '/accounts/login/?next=/assignments/create/'
    selection_template = 'create_assignment.html'
    assignment_template = 'associate_assignment.html'
    shipping_form = ShippingSelectionForm
    date_driver_form = DateDriverForm

    def get(self, request):
        shipping_form = self.shipping_form()
        shipping_objs = shipping_form.fields['shippings'].queryset
        form_set = zip(shipping_form.fields['shippings'].choices, shipping_objs)

        date_driver_form = self.date_driver_form()
        return render(request, self.selection_template, {'form': form_set, 'date_driver_form': date_driver_form})

    def post(self, request):
        shipping_form = self.shipping_form(request.POST)
        date_driver_form = self.date_driver_form(request.POST)
        if shipping_form.is_valid() and date_driver_form.is_valid():
            shipping_assignment_ids = request.POST.getlist('shippings')
            request.session['shipping_assignment_ids'] = shipping_assignment_ids
            request.session['assignment_date'] = request.POST['delivery_date']
            request.session['assignment_driver'] = request.POST['driver']
            return redirect(reverse('deliveries:assignments-associate'))
        return render(request, self.selection_template, {'form': shipping_form})


class AssociateAssignmentsView(LoginRequiredMixin, View):
    login_url = '/accounts/login/?next=/assignments/associate/'
    assignment_template = 'associate_assignment.html'
    form = ShippingAssociateForm

    def get(self, request, *args, **kwargs):
        shipping_assignments = request.session.get('shipping_assignment_ids')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')
        forms = formset_factory(ShippingAssociateForm, extra=len(shipping_assignments))
        formset = forms()
        shipping_assignments_result = Shipping.objects.filter(id__in=shipping_assignments)
        formset_context = []
        for i, form in enumerate(formset):
            form.fields['shipping'].queryset = Shipping.objects.filter(id=shipping_assignments[i])
            formset_context.append([form, shipping_assignments_result[i]])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': len(shipping_assignments)})

    def post(self, request, *args, **kwargs):
        shipping_assignments = request.session.get('shipping_assignment_ids')
        assignment_date = request.session.get('assignment_date')
        assignment_driver = request.session.get('assignment_driver')

        ShippingAssociateFormset = formset_factory(ShippingAssociateForm, extra=len(shipping_assignments))

        shipping_formset = ShippingAssociateFormset(request.POST)
        logger.info(shipping_formset)
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

        shipping_assignments_result = Shipping.objects.filter(id__in=shipping_assignments)
        formset_context = []
        for i, form in enumerate(shipping_formset):
            form.fields['shipping'].queryset = Shipping.objects.filter(id=shipping_assignments[i])
            formset_context.append([form, shipping_assignments_result[i]])

        return render(request, self.assignment_template, {'forms': formset_context, 'assignment_date': assignment_date,
                                                          'assignment_driver': assignment_driver,
                                                          'form_count': len(shipping_assignments)})
