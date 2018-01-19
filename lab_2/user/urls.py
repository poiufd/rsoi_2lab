from django.urls import path
from . import views
from django.conf.urls import include

urlpatterns = [
   	path('check_rights/', views.check_rights),
   	path('check_token/', views.CheckUiToken.as_view(), name = 'check_token'),
   	path('generate_token/<user_id>/', views.GenerateNewToken.as_view(), name = 'generate_token'),
    path('auth/', views.UserLogin.as_view(), name='login'),
    path('<id>/', views.UserView.as_view(), name='user'),
   	path('', views.UsersView.as_view(), name='users'),
]
