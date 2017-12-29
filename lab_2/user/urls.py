from django.urls import path

from . import views

urlpatterns = [
    path('<id>/', views.UserView.as_view(), name='user'),
    path('', views.UsersView.as_view(), name='users')
]