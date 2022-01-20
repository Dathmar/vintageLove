from twilio.rest import Client
from django.conf import settings

import logging
logger = logging.getLogger('app_api')


def quote_notification_text(quote):
    if quote.to_phone:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)

        item_count = int(quote.small_quantity) + int(quote.medium_quantity) + int(quote.large_quantity) + int(quote.set_quantity)
        item_count_text = 'item'
        if item_count > 1:
            item_count_text += 's'

        body = f'''This is Global Vintage Love and we have your shipping quote ready.

CUSTOMER
{quote.to_name}
{quote.to_address}
{quote.to_phone}

SHIPMENT
Item to be picked up from
{quote.from_address}
{item_count} {item_count_text} to be shipped.

QUOTE
${quote.cost} including up to 24' trailer, team of two, fuel and mileage.

Simply click and pay to complete the order and we will schedule the pickup and delivery to you.

globalvintagelove.com/ship/review-quote/{quote.encoding}'''

        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(quote.to_phone)
        )

