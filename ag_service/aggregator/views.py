from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from collections import OrderedDict
from rest_framework.parsers import JSONParser
import requests.exceptions
from rest_framework import status
import logging
from ag_service.celery import app,work_with_products
from django.shortcuts import render
import json
from django.template import loader
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext


url_buys = 'http://localhost:8000/buys/'
url_products = 'http://localhost:8001/products/'
url_user = 'http://localhost:8002/user/'

#logger = logging.getLogger('agg_logger')
logging.basicConfig(filename='temp.log', level=logging.INFO)

class AggUserBuysView(APIView):

    def get(self, request, user_id, order_id, format=None):
        try:
            r = requests.get(url_buys+"user/"+str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            ids = dict.get('products_id')
            list = []

            # here add degradation
            try:
                for id in ids:
                    r = requests.get(url_products+str(id)+"/")
                    list.append(r.json(object_pairs_hook=OrderedDict))
                dict.update({'products_id': list})
            except requests.exceptions.RequestException:
                dict.update({"detail": "Service temporarily unavailable."})
                #return Response(dict, status=status.HTTP_200_OK)
                print(dict)
                render(request, 'order_detail.html', {'result':dict})

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            #return Response(r.json(), status=status_code)
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            #return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return HttpResponse(loader.render_to_string('503.html'), status=503)

        logging.info(u"Show order details")
        #return Response(dict, status=status.HTTP_200_OK)
        return render(request, 'order_detail.html', {'result':dict})


    def post(self, request, user_id, order_id, format=None):
        try:
            r = requests.get(url_buys+"user/"+str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()

            pre_data = request.POST.get("products_id")

            #data = JSONParser().parse(request)

            #data validation
            if not pre_data.isdigit():
                return render(request, 'order_detail.html', {'result':r.json().update({"detail": "Validation error."})} )

            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            #ids = data.get('products_id')
            ids = [int(pre_data)]

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
            logging.info(u"Patch products done")

            #adding here useless get request to show return
            try:
                r = requests.get(url_user+str(user_id)+"/" )    
                r.raise_for_status()
            except requests.exceptions.RequestException:
                #todo
                for id in ids:
                    r = requests.get(url_products + str(id) + "/")
                    temp = r.json(object_pairs_hook=OrderedDict)
                    c = temp.get('count')
                    temp.update({'count': (c+1)})
                    r = requests.patch(url_products + str(id) + "/",temp)
                logging.info(u"Patch products reversed")    
                #return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE) 
                return HttpResponse(loader.render_to_string('503.html'), status=503)   


            dict.update({'products_id': prev_id})
            r = requests.patch(url_buys+ str(order_id) + "/", dict)
            r.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            #return Response(r.json(), status=status_code)
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            #return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return HttpResponse(loader.render_to_string('503.html'), status=503) 

        logging.info(u"Edit order details")
        #return Response(r.json())
        return render(request, 'success.html', {'result':r.json()})


class AggDeleteOrder(APIView):

    def post(self, request, user_id, order_id, product_id, format=None):
        try:
            r = requests.get(url_buys +"user/"+ str(user_id)+"/" + str(order_id)+"/")
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            product_id = int(product_id)
            prev_id = list(map(int, prev_id))

            if product_id in prev_id:
                prev_id.remove(product_id)
                dict.update({'products_id': prev_id})
                r = requests.patch(url_buys + str(order_id) + "/", dict)
                r.raise_for_status()
                work_with_products.delay(product_id)

            else:
                return Response({"detail": "Id not found."})

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return Response(r.json(), status=status_code)
        except requests.exceptions.RequestException:
            return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        logging.info(u"Delete product from order")
        return Response(r.json())

class AggUserAllBuysView(APIView):

    #renderer_classes = [TemplateHTMLRenderer]
    #template_name = 'index.html'

    def get(self, request, user_id, format=None):
        try:
            r = requests.get(url_buys+"user/"+str(user_id)+"/")
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            #return Response(r.json(), status=status_code)
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            #return Response({"detail": "Service temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return HttpResponse(loader.render_to_string('503.html'), status=503)
        logging.info(u"Show orders")
        #return Response(r.json(object_pairs_hook=OrderedDict), status=status.HTTP_200_OK)
        #return Response({'result':r.json(object_pairs_hook=OrderedDict)})
        return render(request, 'orders.html', {'result':r.json(object_pairs_hook=OrderedDict)})
