from django.urls import path
from . import views

urlpatterns = [
    path('<id>/', views.BuyView.as_view(), name='buy'),
    path('', views.BuysView.as_view(), name='buys')
]