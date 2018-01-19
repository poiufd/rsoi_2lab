from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserUiAcc

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', )

class UserUiAccSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserUiAcc
        fields = ('id','user_id', 'token','res_time' )
