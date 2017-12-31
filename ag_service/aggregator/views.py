from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from collections import OrderedDict
from rest_framework.parsers import JSONParser
import requests.exceptions
from rest_framework import status
import logging

url_buys = 'http://localhost:8000/buys/'
url_products = 'http://localhost:8001/products/'
url_user = 'http://localhost:8002/user/'

logger = logging.getLogger('agg_logger')


class AggUserBuysView(APIView):

    def get(self, request, user_id, order_id, format=None):
        try:
            r = requests.get(url_buys+str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            ids = set(dict.get('products_id'))
            list = []

            # here add degradation
            try:
                for id in ids:
                    r = requests.get(url_products+str(id)+"/")
                    list.append(r.json(object_pairs_hook=OrderedDict))
                dict.update({'products_id': list})
            except requests.exceptions.RequestException:
                dict.update({"detail": "Service temporarily unavailable."})
                return Response(dict, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(r.json(), status=status_code)
        except requests.exceptions.RequestException:
            return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info(u"Show order details")
        return Response(dict, status=status.HTTP_200_OK)

    def patch(self, request, user_id, order_id, format=None):
        try:
            r = requests.get(url_buys+str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()
            data = JSONParser().parse(request)
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            ids = data.get('products_id')

            for id in ids:
                r = requests.get(url_products + str(id) + "/")
                r.raise_for_status()
                temp = r.json(object_pairs_hook=OrderedDict)
                c = temp.get('count')
                if c > 0:
                    temp.update({'count': (c-1)})

                    r = requests.patch(url_products + str(id) + "/",temp)
                    r.raise_for_status()
                    prev_id.append(id)
                else:
                    return Response({"detail": "Product is not available."})

            dict.update({'products_id': prev_id})
            r = requests.patch(url_buys+ str(order_id) + "/", dict)
            r.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(r.json(), status=status_code)
        except requests.exceptions.RequestException:
            return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info(u"Edit order details")
        return Response(r.json())


class AggDeleteOrder(APIView):

    def patch(self, request, user_id, order_id, product_id, format=None):
        try:
            r = requests.get(url_buys + str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            product_id = int(product_id)
            prev_id = list(map(int, prev_id))

            try:
                if product_id in prev_id:
                    r = requests.get(url_products + str(product_id) + "/")
                    r.raise_for_status()
                    temp = r.json(object_pairs_hook=OrderedDict)
                    c = temp.get('count')
                    temp.update({'count': (c + 1)})
                    r = requests.patch(url_products + str(product_id) + "/", temp)
                    r.raise_for_status()
                    prev_id.remove(product_id)

                else:
                    return Response({"detail": "Id not found."})

                dict.update({'products_id': prev_id})
                r = requests.patch(url_buys + str(order_id) + "/", dict)
                r.raise_for_status()
            except requests.exceptions.RequestException:
                #tod0 queue

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(r.json(), status=status_code)
        except requests.exceptions.RequestException:
            return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logger.info(u"Delete product from order")
        return Response(r.json())
