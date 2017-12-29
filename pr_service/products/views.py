from .models import Product
from rest_framework.parsers import JSONParser
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

class ProductView(APIView):

    def get(self, request, id, format=None):
        try:
            product = Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

        serializer = ProductSerializer(product)
        return Response(serializer.data)


class ProductsView(APIView):

    def get(self, request, format=None):

        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)

