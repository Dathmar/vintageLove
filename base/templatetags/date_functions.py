from django import template
from datetime import datetime
from pytz import timezone

import logging
register = template.Library()
logger = logging.getLogger('app_api')


@register.filter
def days_from(date):
    return (timezone('UTC').localize(datetime.now()) - date).days

