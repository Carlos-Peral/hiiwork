from django.urls import path, include
from apps.chat import views

urlpatterns = [
    # path('chat/',
    #     views.ChatHome.as_view(), name='chats-home'),
    path('<orderID>/',
         views.OrderChat.as_view(), name='order-chat'),
    # path('order/<userID>/',
    #     views.OrderRequirements.as_view(), name='user-chat'),

]
