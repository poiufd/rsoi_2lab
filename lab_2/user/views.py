from django.contrib.auth.models import User
from .models import UserUiAcc
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer,UserUiAccSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template import RequestContext
from django.shortcuts import render,redirect
import requests 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from braces.views import CsrfExemptMixin
from django.contrib.auth import authenticate
from oauth2_provider.decorators import protected_resource
from django.contrib.auth.decorators import login_required
import binascii
import os
from django.http import HttpResponse, HttpResponseRedirect
import time

exp_time = 60

@protected_resource()
def check_rights(request):
    return HttpResponse(status=200)

def generate_key():
    token = binascii.hexlify(os.urandom(20)).decode() 
    return token     

class CheckUiToken(CsrfExemptMixin,APIView):
    authentication_classes = []

    def get(self,request):
        t = request.META.get('HTTP_AUTHORIZATION')
        print(t)
        try:
            token = UserUiAcc.objects.get(token=t)
        except UserUiAcc.DoesNotExist:
            return Response(status =status.HTTP_403_FORBIDDEN)

        print('succ')
        res_time = token.res_time
        print (abs(time.time() - float(res_time)))
        if abs(time.time() - float(res_time)) >= exp_time:
            return Response(status =status.HTTP_403_FORBIDDEN) 
        else:
            UserUiAcc.objects.filter(token=t).update(res_time=time.time())
            return Response(status =status.HTTP_200_OK)

class GenerateNewToken(CsrfExemptMixin,APIView):
    authentication_classes = []    

    def get(self,request, user_id):
        try:
            user = UserUiAcc.objects.get(user_id=user_id)
        except UserUiAcc.DoesNotExist:
            return Response(status =status.HTTP_403_FORBIDDEN)

        token = generate_key()
        res_time = time.time()

        print(token)
        UserUiAcc.objects.filter(user_id=user_id).update(token = token,res_time=res_time)
        return Response({'Token': token},status =status.HTTP_200_OK)


          

class UserLogin(CsrfExemptMixin,APIView):
    authentication_classes = []

    def get(self,request, *args, **kwargs):

        clientId= request.GET.get('clientId')
        return render(request, 'registration/login.html', {'result':{'clientId':clientId}})


    def post(self,request):
        login = request.POST.get("login")
        password = request.POST.get("password")
        clientId = request.GET.get("clientId")

        user = authenticate(username=login, password=password)
        if user is not None:
            user = User.objects.get(username=login)
            #create ui token
            token = generate_key()
            print(token)

            res_time = time.time()
            print (res_time)
            if UserUiAcc.objects.filter(user_id=user.id).exists(): 
                UserUiAcc.objects.filter(user_id=user.id).delete() 
            
            user_ui_acc = UserUiAcc.objects.create_new(user_id = user.id,token = token, res_time = res_time) 


            r = HttpResponseRedirect('http://localhost:8002/o/authorize/?response_type='
                            'code&client_id={}&username={}&password={}&redirect_uri=http://localhost:8003/auth/'.format(clientId,login,password))
            r.set_cookie('id',user.id)
            r.set_cookie('ui_token',token)
            return r
        else:
            #raise Http404 
            return render(request, 'registration/login.html', {'result':{'error':'Invalid password or login', 'clientId': clientId}})    

class UserView(APIView):

    def get(self, request, id, format=None):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            raise Http404("Not found")

        serializer = UserSerializer(user)
        return Response(serializer.data)

class UsersView(APIView):

    def get(self, request, format=None):
        user = User.objects.all()

        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
