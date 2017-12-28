from django.urls import path

from . import views

urlpatterns = [
    path('<login>/', views.UserView.as_view(), name='user'),
    path('', views.NewView.as_view(), name='add_user')
]