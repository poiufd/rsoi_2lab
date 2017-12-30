from .models import Buy
from rest_framework.parsers import JSONParser
from .serializers import BuySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.paginator import Paginator


class BuyView(APIView):

    def get_object(self, id):

        try:
            return Buy.objects.get(id=id)
        except Buy.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):

        buy = self.get_object(id)
        serializer = BuySerializer(buy)
        return Response(serializer.data)

    def delete(self, request, id, format=None):

        buy = self.get_object(id)
        buy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, id, format=None):

        buy = self.get_object(id)
        serializer = BuySerializer(buy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BuysView(APIView):

    def get(self, request, format=None):

        buy = Buy.objects.all()

        paginator = Paginator(buy, 2)

        page = request.GET.get('page')
        data = paginator.get_page(page)
        if page is not None:
            serializer = BuySerializer(data, many=True)
            return Response(serializer.data)

        serializer = BuySerializer(buy, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        data = JSONParser().parse(request)
        serializer = BuySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
