from django.urls import path

from . import views

urlpatterns = [
    path('<id>/', views.ProductView.as_view(), name='product'),
    path('', views.ProductsView.as_view(), name='products')
]