from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from collections import OrderedDict
from rest_framework.parsers import JSONParser
import requests.exceptions
from django.http import Http404
from rest_framework import status

url_buys = 'http://localhost:8000/buys/'
url_products = 'http://localhost:8001/products/'
url_user = 'http://localhost:8002/user/'


class AggUserBuysView(APIView):

    def get(self, request, order_id, format=None):

        try:
            r = requests.get(url_buys+str(order_id)+"/")
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(status=status_code)

        dict = r.json(object_pairs_hook=OrderedDict)
        ids = set(dict.get('products_id'))
        list = []

        for id in ids:
            r1 = requests.get(url_products+str(id)+"/")
            list.append(r1.json(object_pairs_hook=OrderedDict))
        dict.update({'products_id': list})
        return Response(dict, status=status.HTTP_200_OK)


class AggUpdateOrder(APIView):

    def patch(self, request, user_id, order_id, format=None):
        try:
            r = requests.get(url_buys + str(order_id) + "/")
            r.raise_for_status()
            data = JSONParser().parse(request)
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            if int(dict.get('user_id')) != int(user_id):
                raise Http404
            ids = data.get('products_id')

            for id in ids:
                r1 = requests.get(url_products + str(id) + "/")
                r1.raise_for_status()
                temp = r1.json(object_pairs_hook=OrderedDict)
                c = temp.get('count')
                if c > 0:
                    temp.update({'count': (c-1)})

                    r2 = requests.patch(url_products + str(id) + "/",temp)
                    r2.raise_for_status()
                prev_id.append(id)
                #else:
                #    return count = 0

            dict.update({'products_id': prev_id})
            r3 = requests.patch(url_buys+ str(order_id) + "/", dict)
            r3.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(status=status_code)
        return Response(r.json())


class AggDeleteOrder(APIView):

    def patch(self, request, user_id, order_id, product_id, format=None):

        try:
            r = requests.get(url_buys + str(order_id) + "/")
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            if int(dict.get('user_id')) != int(user_id):
                raise Http404
            product_id = int(product_id)
            prev_id = list(map(int, prev_id))

            if product_id in prev_id:
                r = requests.get(url_products + str(product_id) + "/")
                r.raise_for_status()
                temp = r.json(object_pairs_hook=OrderedDict)
                c = temp.get('count')
                temp.update({'count': (c + 1)})
                r = requests.patch(url_products + str(product_id) + "/", temp)
                r.raise_for_status()
                prev_id.remove(product_id)

            # else:
            #    return count = 0

            dict.update({'products_id': prev_id})
            r = requests.patch(url_buys + str(order_id) + "/", dict)
            r.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(status=status_code)
        return Response(r.json())
