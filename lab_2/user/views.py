from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer
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

class UserLogin(CsrfExemptMixin,APIView):
    authentication_classes = []

    def get(self,request, *args, **kwargs):

        clientId= request.GET.get('clientId')
        return render(request, 'registration/login.html', {'result':{'clientId':clientId}})
        #return HttpResponse(loader.render_to_string('registration/login.html'))

    def post(self,request):
        login = request.POST.get("login")
        password = request.POST.get("password")
        clientId = request.GET.get("clientId")

        #try:
            #user = User.objects.get(username=login,password=password)
        #except User.DoesNotExist:
        #    raise Http404
        user = authenticate(username=login, password=password)
        if user is not None:

        #response = requests.post('http://localhost:8002/o/token/', data=data, auth=(clientId,  clientSecret))
    
        #return Response(response)
            user = User.objects.get(username=login)
            r = HttpResponseRedirect('http://localhost:8002/o/authorize/?response_type='
                            'code&client_id={}&username={}&password={}&redirect_uri=http://localhost:8003/auth/'.format(clientId,login,password))
            r.set_cookie('id',user.id)
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
