from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.auth, name='auth'),
    path('user/<user_id>/order/<order_id>/', views.AggUserBuysView.as_view(), name='agg1'),
    path('user/<user_id>/orders/', views.AggUserAllBuysView.as_view(), name='agg2'),
    path('user/<user_id>/order/<order_id>/product/<product_id>/', views.AggDeleteOrder.as_view(), name='agg3'),
    path('', views.UserLogin.as_view(), name='index'),

]
