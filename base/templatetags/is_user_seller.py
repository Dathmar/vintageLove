from django import template
from products.models import UserSeller

register = template.Library()


@register.filter
def is_seller(user):
    if user.is_authenticated:
        if UserSeller.objects.filter(user=user).exists():
            return True
    return False
