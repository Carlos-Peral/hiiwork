from django import template

from allauth.account.utils import user_display
from apps.profiles.models import UserProfile


register = template.Library()


@register.simple_tag(name='user_display')
def user_display_tag(user):
    """
    Example usage::

        {% user_display user %}

    or if you need to use in a {% blocktrans %}::

        {% user_display user as user_display %}
        {% blocktrans %}
        {{ user_display }} has sent you a gift.
        {% endblocktrans %}

    """
    return user_display(user)


@register.simple_tag
def user_profile(user):
    """
    This returns the request user profile.
    """
    profile = UserProfile.objects.get(user=user)
    return profile
