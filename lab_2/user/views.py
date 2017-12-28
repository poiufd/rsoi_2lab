from .models import User
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


class UserView(APIView):

    def get(self, request, login, format=None):
        try:
            user = User.objects.get(login=login)
        except User.DoesNotExist:
            raise Http404

        serializer = UserSerializer(user)
        return Response(serializer.data)

class NewView(APIView):

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)