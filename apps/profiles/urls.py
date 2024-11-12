from apps.portfolios import views
from django.urls import path

urlpatterns = [
    path('<username>/', views.PortfoliosView.as_view(), name='profile'),
    path('<username>/edit/', views.EditProfileView.as_view(), name='edit_profile'),


]
