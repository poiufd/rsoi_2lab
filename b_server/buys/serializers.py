from rest_framework import serializers
from .models import Buy

class BuySerializer(serializers.ModelSerializer):
    class Meta:
        model = Buy
        fields = ('id', 'number', 'user_id', 'products_id')