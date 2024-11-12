from django.urls import path, include
from apps.orders import views

urlpatterns = [

    path('dashboard/',
         views.OrdersDashboard.as_view(), name='orders-dashboard'),
    path('order/<orderID>/req/<thanks>',
         views.OrderRequirements.as_view(), name='req-thanks'),
    path('order/<orderID>/req/',
         views.OrderRequirements.as_view(), name='req'),
    path('fnz/',
         views.finanzasView.as_view(), name='fnz'),
]
