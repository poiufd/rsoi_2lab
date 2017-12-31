from .models import User
from rest_framework.parsers import JSONParser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


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