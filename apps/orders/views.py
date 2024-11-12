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


class OrdersDashboard(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        context = {}
        orders = Order.objects.filter(buyer=request.user)
        context['orders'] = orders
        return render(request, 'orders/dashboard.html', context=context)

    def post(self, request, *args, **kwargs):
        pass


class OrderRequirements(View):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        try:
            order = get_object_or_404(Order, orderID=kwargs['orderID'])
        except:
            raise SomethingWrongException('Nigga wtf')

        try:
            thanks = False
            if kwargs['thanks'] == 'True':
                thanks = True
        except:
            pass

        # Convert the order string from the url to dict
        context = OrderDecoder.decode(order.orderString)
        # Get the requirements for the gig
        requirements = list(Requirement.objects.filter(
            gig=context['package'].gig))
        # If there are none, redirect to the about pagee
        if len(requirements) == 0:
            redirect('about', orderID=order.orderID, thanks=kwargs['thanks'])

        RequirementClientFactory = modelformset_factory(
            RequirementClient, form=RequirementClientForm, extra=len(requirements), max_num=len(requirements), min_num=len(requirements), validate_min=len(requirements))

        # We need  to make sure there is an existing RequirementClient saven in the DB
        # First we check
        queryset = RequirementClient.objects.filter(order=order)

        if len(list(queryset)) == 0:
            # If not, crete them, and save
            for eachReq in requirements:
                RequirementClient(order=order, requirement=eachReq).save()
            # finally get the queryset again, this time it won't be empty
            queryset = RequirementClient.objects.filter(order=order)

        requirementsClientFormset = RequirementClientFactory(
            queryset=queryset, prefix='Requirements')

        context = {"requirementFormset": requirementsClientFormset,
                   'thanks': thanks}

        return render(request, 'orders/requirements.html', context=context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        try:
            order = get_object_or_404(Order, orderID=kwargs['orderID'])
        except:
            raise SomethingWrongException('Nigga wtf')

        # Convert the order string from the url to dict
        context = OrderDecoder.decode(order.orderString)
        # Get the requirements for the gig
        requirements = list(Requirement.objects.filter(
            gig=context['package'].gig))
        # If there are none, redirect to the About page
        if len(requirements) == 0:
            redirect('about', orderID=order.orderID, thanks=kwargs['thanks'])

        RequirementClientFactory = modelformset_factory(
            RequirementClient, form=RequirementClientForm, extra=len(requirements), max_num=len(requirements), min_num=len(requirements), validate_min=len(requirements))

        requirementsClientFormset = RequirementClientFactory(
            request.POST, request.FILES, prefix='Requirements')

        if requirementsClientFormset.is_valid():
            pass
        else:
            pass

        context = {"requirementFormset": requirementsClientFormset}

        return render(request, 'gigs/requirements.html', context=context)


class finanzasView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'orders/finanzas.html')
