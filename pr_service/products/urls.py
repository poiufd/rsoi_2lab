from django.urls import path

from . import views

urlpatterns = [
	path('get_token/', views.GetToken.as_view(), name = 'get_token'),
	path('check_token/', views.CheckToken.as_view(), name = 'check_token'),	
    path('<id>/', views.ProductView.as_view(), name='product'),
    path('', views.ProductsView.as_view(), name='products')
]
