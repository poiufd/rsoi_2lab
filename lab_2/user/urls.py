from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
    path('auth/', views.UserLogin.as_view(), name='login'),
    path('<id>/', views.UserView.as_view(), name='user'),
   	path('', views.UsersView.as_view(), name='users'),
]
