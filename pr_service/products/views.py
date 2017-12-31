from .models import Product
from rest_framework.parsers import JSONParser
from .serializers import ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.paginator import Paginator

class ProductView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404("Not found")

    def get(self, request, id, format=None):
        product = self.get_object(id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, id, format=None):

        product = self.get_object(id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductsView(APIView):

    def get(self, request, format=None):

        product = Product.objects.all()

        paginator = Paginator(product, 2)
        page = request.GET.get('page')
        data = paginator.get_page(page)
        if page is not None:
            serializer = ProductSerializer(data, many=True)
            return Response(serializer.data)
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)

