from django import template
from apps.gigs.models import Gig, Order
from apps.gigs.utils import OrderDecoder
from apps.profiles.models import UserProfile

register = template.Library()


@register.inclusion_tag('orders/orderRow.html')
def order_row(order):
    orderDetails = order.get_order_details()
    return {
        'orderDetails': orderDetails,
        'order': order
    }
