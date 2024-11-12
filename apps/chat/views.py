from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.views import View
from apps.gigs.forms import *
from apps.gigs.models import Gig, Order, Requirement
from apps.profiles.models import UserProfile
from django.http import Http404
from apps.gigs.utils import OrderDecoder, SomethingWrongException
from apps.orders.OrderManager import OrderManager
from django.conf import settings

# Create your views here.


class OrderChat(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        try:
            order = get_object_or_404(Order, orderID=kwargs['orderID'])
        except:
            raise SomethingWrongException('Nigga wtf')

        # Convert the order string from the url to dict
        context = OrderDecoder.decode(order.orderString)

        context = {"order": order}

        try:
            pass
        except:
            pass

        return render(request, 'chat/order-chat.html', context=context)
