from django.urls import path
from apps.gigs import views

urlpatterns = [
    path('create/', views.CreateGigBasicInfoView.as_view(), name='create'),
    path('create/packages/',
         views.CreateGigPriceAndPackagesView.as_view(), name='packages'),
    path('create/extras/',
         views.CreateExtrasView.as_view(), name='extras'),
    path('create/FAQs/',
         views.CreateFAQsView.as_view(), name='FAQs'),
    path('create/requirements/',
         views.CreateRequirementsView.as_view(), name='requirement'),
    path('details/<int:id>/',
         views.detailedGig.as_view(), name='details'),
    path('checkout/<orderDetails>/',
         views.OrderCheckoutView.as_view(), name='checkout'),
    path('checkout/<orderDetails>/pay',
         views.OrderPayment.as_view(), name='pay'),
]
