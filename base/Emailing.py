import threading
from django.conf import settings
import mailchimp_transactional as mailchimpTransactional
from mailchimp_transactional.api_client import ApiClientError

shipping_create_template_id = '13384681'


def send_quote_paid_notification(quote):
    subject = f'Quote Paid {quote.from_name}'

    if settings.ENVIRONMENT == 'localhost':
        subject = f'!!TESTING!! - {subject}'

    if '123 test ln' in quote.to_address.casefold():
        subject = f'!!TESTING!! - {subject}'

    body = f'''
            A quote was paid

            Details:
            Small items:
            Quantity: {quote.small_quantity}
            Description: {quote.small_description}
            Medium items:
            Quantity: {quote.medium_quantity}
            Description: {quote.medium_description}
            Large items:
            Quantity: {quote.large_quantity}
            Description: {quote.large_description}
            Set items:
            Quantity: {quote.set_quantity}
            Description: {quote.set_description}

            Shipping Origin
            Name: {quote.from_name}
            E-mail: {quote.from_email}
            Phone: {quote.from_phone}
            Address:
            {quote.from_address}

            Shipping Destination
            Name: {quote.to_name}
            E-mail: {quote.to_email}
            Phone: {quote.to_phone}
            Address:
            {quote.to_address}

            '''

    html_body = f"""
                        <!DOCTYPE html>
                        <html>
                            <head>
                            </head>
                            <body>
                                <p>A quote was paid</p>
                                <p></p>
                                <p>Details:</p>
                                <p>Small items:</p>
                                <p>Quantity: {quote.small_quantity}</p>
                                <p>Description: {quote.small_description}</p>
                                <p>Medium items:</p>
                                <p>Quantity: {quote.medium_quantity}</p>
                                <p>Description: {quote.medium_description}</p>
                                <p>Large items:</p>
                                <p>Quantity: {quote.large_quantity}</p>
                                <p>Description: {quote.large_description}</p>
                                <p>Set items:</p>
                                <p>Quantity: {quote.set_quantity}</p>
                                <p>Description: {quote.set_description}</p>
                                <p>Shipping Origin</p>
                                <p>Name: {quote.from_name}</p>
                                <p>E-mail: {quote.from_email}</p>
                                <p>Phone: {quote.from_phone}</p>
                                <p>Address:</p>
                                <p>{quote.from_address}</p>
                                <p></p>
                                <p>Shipping Destination</p>
                                <p>Name: {quote.to_name}</p>
                                <p>E-mail: {quote.to_email}</p>
                                <p>Phone: {quote.to_phone}</p>
                                <p>Address:</p>
                                <p>{quote.to_address}</p>
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


def send_ship_status_email(ShippingOrder, to_status, Delivery=None):
    if to_status == 'created':
        ship_create_email(ShippingOrder)
    elif to_status == 'Pickup Scheduled':
        ship_pickup_scheduled_email(ShippingOrder, Delivery)
    elif to_status == 'Pickup Complete':
        ship_picked_up_email(ShippingOrder)
    elif to_status == 'Out for Delivery':
        ship_out_email(ShippingOrder, Delivery)
    elif to_status == 'Delivery Complete':
        ship_delivered_email(ShippingOrder)


def items_details(ShippingOrder):
    items = ''
    small_quantity = int(ShippingOrder.small_quantity)
    if small_quantity > 0:
        items += str(small_quantity) + ' small '
        if small_quantity == 1:
            items += 'item '
        else:
            items += 'items '
    medium_quantity = int(ShippingOrder.medium_quantity)
    if medium_quantity > 0:
        items += str(medium_quantity) + ' medium '
        if medium_quantity == 1:
            items += 'item '
        else:
            items += 'items '
    large_quantity = int(ShippingOrder.large_quantity)
    if large_quantity > 0:
        items += str(large_quantity) + ' large '
        if large_quantity == 1:
            items += 'item '
        else:
            items += 'items '
    set_quantity = int(ShippingOrder.set_quantity)
    if set_quantity > 0:
        items += str(set_quantity) + ' set '
        if set_quantity == 1:
            items += 'item '
        else:
            items += 'items '

    return items


def insurance_details(ShippingOrder):
    if ShippingOrder.insurance:
        insurance = 'Your order is fully insured.'
    else:
        insurance = 'Your order is insured up to the cost of the service.'
    return insurance


def ship_location_details(ShippingOrder):
    if ShippingOrder.ship_location == 'door':
        ship_location = 'We will provide delivery to your door.'
    else:
        ship_location = 'We place your item in your home.'
    return ship_location


def ship_create_email(ShippingOrder):
    items = items_details(ShippingOrder)
    insurance = insurance_details(ShippingOrder)
    ship_location = ship_location_details(ShippingOrder)

    global_merge_vars = {
        'items': items,
        'from_name': ShippingOrder.from_name,
        'from_address': ShippingOrder.from_address,
        'to_name': ShippingOrder.to_name,
        'to_address': ShippingOrder.to_address,
        'placement': ship_location,
        'insurance': insurance,
    }

    EmailTemplateThread(
        template="Shipping Order - Create",
        recipient=ShippingOrder.to_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def ship_pickup_scheduled_email(ShippingOrder, Delivery):
    items = items_details(ShippingOrder)

    global_merge_vars = {
        'items': items,
        'from_name': ShippingOrder.from_name,
        'from_address': ShippingOrder.from_address,
        'to_name': ShippingOrder.to_name,
        'order_window': Delivery.get_tod_display(),
        'pickup_date': Delivery.scheduled_date.strftime("%m-%d-%Y"),
    }

    EmailTemplateThread(
        template="Shipping Order - Pickup Scheduled",
        recipient=ShippingOrder.from_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def ship_picked_up_email(ShippingOrder):
    global_merge_vars = {
        'from_name': ShippingOrder.from_name,
        'from_address': ShippingOrder.from_address,
        'to_name': ShippingOrder.to_name,
        'to_address': ShippingOrder.to_address,
    }

    EmailTemplateThread(
        template="Shipping Order - Picked Up",
        recipient=ShippingOrder.to_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def quote_notification_email(Quote):
    items = items_details(Quote)
    insurance = insurance_details(Quote)
    ship_location = ship_location_details(Quote)

    global_merge_vars = {
        'items': items,
        'from_name': Quote.from_name,
        'from_address': Quote.from_address,
        'to_name': Quote.to_name,
        'to_address': Quote.to_address,
        'quote_id': str(Quote.encoding),
        'quote_cost': Quote.cost,
        'placement': ship_location,
        'insurance': insurance,
    }

    EmailTemplateThread(
        template="Quote - Created",
        recipient=Quote.to_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def ship_delivered_email(ShippingOrder):
    global_merge_vars = {
        'from_name': ShippingOrder.from_name,
        'from_address': ShippingOrder.from_address,
        'to_name': ShippingOrder.to_name,
        'to_address': ShippingOrder.to_address,
    }

    EmailTemplateThread(
        template="Shipping Order - Thank You",
        recipient=ShippingOrder.to_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def ship_out_email(ShippingOrder, Delivery):
    items = items_details(ShippingOrder)
    insurance = insurance_details(ShippingOrder)
    ship_location = ship_location_details(ShippingOrder)

    global_merge_vars = {
        'items': items,
        'order_window': Delivery.get_tod_display(),
        'to_address': ShippingOrder.to_address,
        'placement': ship_location,
        'insurance': insurance,
    }

    EmailTemplateThread(
        template="Shipping Order - On the Way",
        recipient=ShippingOrder.to_email,
        global_merge_vars_dict=global_merge_vars,
    ).start()


def send_internal_shipping_notification(shipping):
    subject = f'New Shipping Order Received for {shipping.from_name}'

    if settings.ENVIRONMENT == 'localhost':
        subject = f'!!TESTING!! - {subject}'

    if '123 test ln' in shipping.to_address.casefold():
        subject = f'!!TESTING!! - {subject}'

    body = f'''
        We have a new shipping order

        Details:
        Small items:
        Quantity: {shipping.small_quantity}
        Description: {shipping.small_description}
        Medium items:
        Quantity: {shipping.medium_quantity}
        Description: {shipping.medium_description}
        Large items:
        Quantity: {shipping.large_quantity}
        Description: {shipping.large_description}
        Set items:
        Quantity: {shipping.set_quantity}
        Description: {shipping.set_description}

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
                            <p>Details:</p>
                            <p>Small items:</p>
                            <p>Quantity: {shipping.small_quantity}</p>
                            <p>Description: {shipping.small_description}</p>
                            <p>Medium items:</p>
                            <p>Quantity: {shipping.medium_quantity}</p>
                            <p>Description: {shipping.medium_description}</p>
                            <p>Large items:</p>
                            <p>Quantity: {shipping.large_quantity}</p>
                            <p>Description: {shipping.large_description}</p>
                            <p>Set items:</p>
                            <p>Quantity: {shipping.set_quantity}</p>
                            <p>Description: {shipping.set_description}</p>
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


class EmailTemplateThread(threading.Thread):
    def __init__(self, template, recipient, global_merge_vars_dict):
        self.template = template
        self.recipient = recipient
        self.global_merge_vars = [{"name": key, "content": value} for key, value in global_merge_vars_dict.items()]
        threading.Thread.__init__(self)

    def run(self):
        mailchimp = mailchimpTransactional.Client(settings.EMAIL_HOST_PASSWORD)
        send_template = {
            'template_name': self.template,
            'template_content': [],
            'message': {
                "from_email": settings.EMAIL_HOST_USER,
                "to": [
                    {
                        "email": self.recipient,
                        "type": "to"
                    }
                ],
                "global_merge_vars": self.global_merge_vars,
            },

        }

        try:
            response = mailchimp.messages.send_template(send_template)
            print(f'API called successfully: {response}')
        except ApiClientError as error:
            print(f'An exception occurred: {error.text}')


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient, from_email, fail_silently, html_message):
        self.subject = subject
        self.recipient = recipient
        self.message = message
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        mailchimp = mailchimpTransactional.Client(settings.EMAIL_HOST_PASSWORD)
        message = {
            "from_email": self.from_email,
            "subject": self.subject,
            "text": self.message,
            "html": self.html_message,
            "to": [
                {
                    "email": self.recipient,
                    "type": "to"
                }
            ]
        }

        try:
            response = mailchimp.messages.send({"message": message})
            print(f'API called successfully: {response}')
        except ApiClientError as error:
            print(f'An exception occurred: {error.text}')
