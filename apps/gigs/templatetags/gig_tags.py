from django import template
from apps.gigs.models import Gig

register = template.Library()


@register.inclusion_tag('gigs/gigCard.html')
def gig_card(gig):
    return {
        'gig': gig,
    }
