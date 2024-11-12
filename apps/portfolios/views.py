from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from apps.profiles.models import UserProfile
from apps.portfolios.models import Portfolio
from apps.gigs.models import Gig
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime


class PortfoliosView(View):
    def get(self, request, *args, **kwargs):
        # Get the requested profile if it exists.
        profile = get_object_or_404(
            UserProfile, user__username=kwargs['username'])
        context = {'profile': profile}
        # We need the timestamp because of the CORS bug between AWS S3 and Chrome
        timestamp = int(datetime.timestamp(datetime.now()))
        context['timestamp'] = timestamp
        # Check if the profile has a portfolio
        try:
            portfolio = Portfolio.objects.get(
                user=profile.user)
            context['portfolio'] = portfolio
            gigs = Gig.objects.filter(author=profile.user, isActive=True)
            context['gigs'] = gigs
        except ObjectDoesNotExist:
            # If the profile doesn't have a portfolio, it's a buyer. Render the respective view.
            return render(request, 'portfolios/buyerProfile.html', context=context)
        # The profile has a portfolio. Render the respective view.
        return render(request, 'portfolios/portfolio.html', context=context)

    def post(self, request, *args, **kwargs):
        return HttpResponse('POST request!')


class EditProfileView(View):
    def get(self, request, *args, **kwargs):
        # Get the requested profile if it exists.
        profile = get_object_or_404(
            UserProfile, user__username=kwargs['username'])
        context = {'profile': profile}
        # Check if the user who want's to edit is the same as the profile owner.
        if profile.user == request.user:
            # If they are, render the edit view.
            return render(request, 'portfolios/editProfile.html', context=context)
        else:
            # If they are not, redirect to the profile page
            return redirect(('/user/%s') % kwargs['username'])

    def post(self, request, *args, **kwargs):
        pass
