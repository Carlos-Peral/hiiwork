from django.contrib import admin
from apps.portfolios.models import *

admin.site.register(Portfolio, admin.ModelAdmin)
