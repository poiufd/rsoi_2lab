from django.urls import path
from . import views

urlpatterns = [
    path('<id>/', views.BuyView.as_view(), name='buy'),
    path('', views.BuysView.as_view(), name='buys'),
    path('user/<user_id>/<buy_id>/', views.BuysByUserView.as_view(), name='buy_user'),
    path('user/<user_id>/', views.AllBuysByUserView.as_view(), name='all_buy_user')
]