from .models import Product
from rest_framework.parsers import JSONParser
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.paginator import Paginator
import binascii
import os
from django.http import HttpResponse, HttpResponseRedirect
import time

#aggregator clientid,secret
ClientId = 'OdDr0vDribM42njMOQwmakhGC1vXaTogVyipMHjK'
ClientSecret = '0RoojuHswkIMfhPLt38yo2jIyjZzf9NZunMR8hcVm0e6h2nJrTDDM607ZNpRjZud5hjuMEo5NOR80ZG6e4dVkVDkJdLLZblf5B8mKBCBQVNfuZqi92CGzeibqofvQh3v'
token = ''
res_time = 0

#expired time in seconds
exp_time = 60

def generate_key():
    global token
    global res_time
    token = binascii.hexlify(os.urandom(20)).decode() 
    res_time = time.time()
    return token     

def check_token(request):
    t = request.META.get('HTTP_AUTHORIZATION')
    if t != token:
        return False
    elif (abs(time.time() - res_time) >= exp_time):
        return False
    else:
        return True           

class GetToken(APIView):

    def get(self,request):
        client_id = request.GET.get("clientId")
        client_secret = request.GET.get("clientSecret")
        if client_id == ClientId and ClientSecret == client_secret:
            return Response({"Token":generate_key()}) 
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)    


class CheckToken(APIView):

    def get(self,request):
        t = request.META.get('HTTP_AUTHORIZATION')
        print(t)
        print(token)
        if t != token:
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif (abs(time.time() - res_time) >= exp_time):
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status = status.HTTP_200_OK)    


class ProductView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404("Not found")

    def get(self, request, id, format=None):
        if check_token(request):
            product = self.get_object(id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)             

    def patch(self, request, id, format=None):
        if check_token(request):
            product = self.get_object(id)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)         


class ProductsView(APIView):

    def get(self, request, format=None):
        if check_token(request):
            product = Product.objects.all()

            paginator = Paginator(product, 2)
            page = request.GET.get('page')
            data = paginator.get_page(page)
            if page is not None:
                serializer = ProductSerializer(data, many=True)
                return Response(serializer.data)
            serializer = ProductSerializer(product, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)            

