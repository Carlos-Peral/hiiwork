from allauth.account.views import SignupView
from allauth.account.forms import LoginForm
from django.shortcuts import HttpResponse, render
from django.views import View
from apps.profiles.models import UserProfile


class Home(View):
    def get(self, request):
        context = {}
        return render(request, 'mainPage/homepage.html', context=context)
