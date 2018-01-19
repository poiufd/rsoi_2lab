from rest_framework.views import APIView
import requests
from collections import OrderedDict
from rest_framework.parsers import JSONParser
import requests.exceptions
import logging
from ag_service.celery import app,work_with_products
from django.shortcuts import render,redirect
import json
from django.template import loader
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from braces.views import CsrfExemptMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

url_buys = 'http://localhost:8000/buys/'
url_products = 'http://localhost:8001/products/'
url_user = 'http://localhost:8002/user/'
url_aggregator = 'http://localhost:8003/'

logging.basicConfig(filename='temp.log', level=logging.INFO)

ClientId = 'OdDr0vDribM42njMOQwmakhGC1vXaTogVyipMHjK'
ClientSecret = '0RoojuHswkIMfhPLt38yo2jIyjZzf9NZunMR8hcVm0e6h2nJrTDDM607ZNpRjZud5hjuMEo5NOR80ZG6e4dVkVDkJdLLZblf5B8mKBCBQVNfuZqi92CGzeibqofvQh3v'
BuysToken = 'None'
ProductsToken = 'None'

def has_access(request):
    token = request.COOKIES.get('access')

    headers = {
                'Authorization': 'Bearer '+ str(token),
                }
    r = requests.get(url_user + 'check_rights/', headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False

def has_access_ui(request):
    ui_token = request.COOKIES.get('ui_token')
    print('ui_token')
    print(ui_token)
    headers = make_header(ui_token)

    r = requests.get(url_user + 'check_token/', headers=headers)
    if r.status_code == 200:
        return True
    else:
        return False

def make_header(token):
    headers = {
                'Authorization': str(token),
                }   
    return headers
                  
def has_access_service(url,token):
    headers = make_header(token)
    r = requests.get(url + 'check_token/', headers=headers)   
    if r.status_code == 200:
        return True
    else:
        return False               

def get_token(url):
    global BuysToken
    global ProductsToken
    r = requests.get(url +"get_token/?clientId={}&clientSecret={}".format(ClientId,ClientSecret)) 
    if r.status_code == 200:
        if url == url_buys:
            BuysToken = r.json().get('Token')
        else:
            ProductsToken = r.json().get('Token')           
        return True 
    else:
        return False       

def refresh(request):
    try:
        r = requests.get(url_aggregator+'re_auth/',cookies=request.COOKIES)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return False
    return True        

def refresh_ui(request,id):
    try:
        r = requests.get(url_user+'generate_token/'+str(id),cookies=request.COOKIES)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:  
        return None
    return r.json().get('Token')    

class ReAuth(CsrfExemptMixin,APIView):
    authentication_classes = []
    
    def get(self,request): 
        try:
            token = request.COOKIES.get('refresh')
            r = requests.post('http://localhost:8002/o/token/?grant_type=refresh_token&'
                                        'client_id={}&client_secret={}&refresh_token={}&redirect_uri=http://localhost:8003/re_auth/'.format(ClientId ,ClientSecret,token))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return HttpResponse(status=status_code)

        r1 = HttpResponse()
        r1.set_cookie('access',r.json().get('access_token'))
        r1.set_cookie('refresh',r.json().get('refresh_token'))

        return r1

class UserLogin(CsrfExemptMixin,APIView):
    authentication_classes = []
    def get(self, request):
        return HttpResponse(loader.render_to_string('index.html'))


class Auth(CsrfExemptMixin,APIView):
    authentication_classes = []
    
    def get(self,request): 
        try:
            r = requests.post('http://localhost:8002/o/token/?grant_type=authorization_code&'
                                        'client_id={}&client_secret={}&code={}&redirect_uri=http://localhost:8003/auth/'.format(ClientId ,ClientSecret,request.GET.get('code')))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
    
        user_id = request.COOKIES.get('id')

        r1 = HttpResponseRedirect(reverse('agg2',args=[user_id]))
        r1.set_cookie('access',r.json().get('access_token'))
        r1.set_cookie('refresh',r.json().get('refresh_token'))        

        #here redirect to userid
        return r1


class Auth2(CsrfExemptMixin,APIView):
    authentication_classes = []
    
    def get(self,request):
        return HttpResponse('Success')


class AggUserBuysView(CsrfExemptMixin,APIView):
    authentication_classes = []
    
    def get(self, request, user_id, order_id, format=None):
        if not has_access(request):
            if not refresh(request): 
                return HttpResponseRedirect(url_aggregator)
        
        token = None
        if not has_access_ui(request):
            r = refresh_ui(request,user_id)
            if r:
                token = r 
                print(token)   
            else:
                return HttpResponse(loader.render_to_string('403.html'), status=403)            
            
        try:
            r = requests.get(url_buys+"user/"+str(user_id)+"/" + str(order_id)+"/", headers = make_header(BuysToken))
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            ids = dict.get('products_id')
            list = []
            # here add degradation
            try:
                for id in ids:
                    r = requests.get(url_products+str(id)+"/",headers = make_header(ProductsToken))
                    r.raise_for_status()
                    list.append(r.json(object_pairs_hook=OrderedDict))
                dict.update({'products_id': list})
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 403:
                    if get_token(url_products):
                        r = redirect('agg1', user_id= user_id, order_id=order_id)
                        if token != None: 
                            r.set_cookie('ui_token',token)
                        return r
                else:                             
                    return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)    
            except requests.exceptions.RequestException:
                dict.update({"detail": "Service temporarily unavailable."})
                return render(request, 'order_detail.html', {'result':dict})

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                if get_token(url_buys):
                    r = redirect('agg1', user_id= user_id, order_id=order_id)
                    if token != None:  
                        r.set_cookie('ui_token',token)
                    return r
            else:                             
                return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            return HttpResponse(loader.render_to_string('503.html'), status=503)

        logging.info(u"Show order details")

        r = render(request, 'order_detail.html', {'result':dict})
        if token != None:  
            r.set_cookie('ui_token',token)
        return r


    def post(self, request, user_id, order_id, format=None):
        if not has_access(request):
            if not refresh(request): 
                return HttpResponseRedirect(url_aggregator)

        token = None
        if not has_access_ui(request):
            r = refresh_ui(request,user_id)
            if r:
                token = r 
                print(token)   
            else:
                return HttpResponse(loader.render_to_string('403.html'), status=403)

        try:
            try:
                r = requests.get(url_buys+"user/"+str(user_id)+"/" + str(order_id)+"/",headers = make_header(BuysToken))
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 403:
                    if get_token(url_buys):
                        r = requests.get(url_buys+"user/"+str(user_id)+"/" + str(order_id)+"/",headers = make_header(BuysToken))
                        r.raise_for_status()
                    else:                             
                        return HttpResponse(loader.render_to_string('403.html'), status=403)      
            r.raise_for_status()            

            pre_data = request.POST.get("products_id")

            #data validation
            if not pre_data.isdigit():
                return render(request, 'order_detail.html', {'result':r.json().update({"detail": "Validation error."})} )

            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            ids = [int(pre_data)]

            for id in ids:
                try:
                    r = requests.get(url_products + str(id) + "/",headers = make_header(ProductsToken))
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code
                    if status_code == 403:
                        if get_token(url_products):
                            r = requests.get(url_products + str(id) + "/",headers = make_header(ProductsToken))
                            r.raise_for_status()
                        else:                             
                            return HttpResponse(loader.render_to_string('403.html'), status=403)      
                r.raise_for_status()                                
                temp = r.json(object_pairs_hook=OrderedDict)
                c = temp.get('count')
                if c > 0:
                    temp.update({'count': (c-1)})
                    try:
                        r = requests.patch(url_products + str(id) + "/",temp,headers = make_header(ProductsToken))
                        r.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        status_code = e.response.status_code
                        if status_code == 403:
                            if get_token(url_products):
                                r = requests.patch(url_products + str(id) + "/",temp,headers = make_header(ProductsToken))
                                r.raise_for_status()
                            else:                             
                                return HttpResponse(loader.render_to_string('403.html'), status=403)  
                    r.raise_for_status()                
                    prev_id.append(id)
            logging.info(u"Patch products done")

            #adding here useless get request to show return
            try:
                r = requests.get(url_user+str(user_id)+"/" )    
                r.raise_for_status()
            except requests.exceptions.RequestException:
                for id in ids:
                    try:
                        r = requests.get(url_products + str(id) + "/",headers = make_header(ProductsToken))
                        r.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        status_code = e.response.status_code
                        if status_code == 403:
                            if get_token(url_products):
                                r = requests.get(url_products + str(id) + "/",headers = make_header(ProductsToken))
                                r.raise_for_status()
                            else:                             
                                return HttpResponse(loader.render_to_string('403.html'), status=403)      
                    r.raise_for_status()                                
                    temp = r.json(object_pairs_hook=OrderedDict)
                    c = temp.get('count')
                    temp.update({'count': (c+1)})
                    try:
                        r = requests.patch(url_products + str(id) + "/",temp,headers = make_header(ProductsToken))
                        r.raise_for_status()
                    except requests.exceptions.HTTPError as e:
                        status_code = e.response.status_code
                        if status_code == 403:
                            if get_token(url_products):
                                r = requests.patch(url_products + str(id) + "/",temp,headers = make_header(ProductsToken))
                                r.raise_for_status()
                            else:                             
                                return HttpResponse(loader.render_to_string('403.html'), status=403)  

                logging.info(u"Patch products reversed")    
                return HttpResponse(loader.render_to_string('503.html'), status=503)   

            dict.update({'products_id': prev_id})
            try:
                r = requests.patch(url_buys+ str(order_id) + "/", dict,headers = make_header(BuysToken))
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 403:
                    if get_token(url_buys):
                        r = requests.patch(url_buys+ str(order_id) + "/", dict,headers = make_header(BuysToken))
                        r.raise_for_status()
                    else:                             
                        return HttpResponse(loader.render_to_string('403.html'), status=403)      
            r.raise_for_status()                          

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            return HttpResponse(loader.render_to_string('503.html'), status=503) 

        logging.info(u"Edit order details")
        r = redirect('agg1', user_id= user_id, order_id=order_id)
        if token != None:  
            r.set_cookie('ui_token',token)
        return r

class AggDeleteOrder(CsrfExemptMixin,APIView):
    authentication_classes = []

    def post(self, request, user_id, order_id, product_id, format=None):
        if not has_access(request):
            if not refresh(request): 
                return HttpResponseRedirect(url_aggregator)

        token = None
        if not has_access_ui(request):
            r = refresh_ui(request,user_id)
            if r:
                token = r 
                print(token)   
            else:
                return HttpResponse(loader.render_to_string('403.html'), status=403)

        try:
            try:
                r = requests.get(url_buys +"user/"+ str(user_id)+"/" + str(order_id)+"/",headers = make_header(BuysToken))
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 403:
                    if get_token(url_buys):
                        r = requests.get(url_buys +"user/"+ str(user_id)+"/" + str(order_id)+"/",headers = make_header(BuysToken))
                        r.raise_for_status()
                    else:                             
                        return HttpResponse(loader.render_to_string('403.html'), status=403)  
            r.raise_for_status()
            dict = r.json(object_pairs_hook=OrderedDict)
            prev_id = dict.get('products_id')
            product_id = int(product_id)
            prev_id = list(map(int, prev_id))

            if product_id in prev_id:
                prev_id.remove(product_id)
                dict.update({'products_id': prev_id})
                try:
                    r = requests.patch(url_buys + str(order_id) + "/", dict,headers = make_header(BuysToken))
                    r.raise_for_status()
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code
                    if status_code == 403:
                        if get_token(url_buys):
                            r = requests.get(url_buys +"user/"+ str(user_id)+"/" + str(order_id)+"/",headers = make_header(BuysToken))
                            r.raise_for_status()
                        else:                             
                            return HttpResponse(loader.render_to_string('403.html'), status=403)  
                r.raise_for_status()                    
                r = work_with_products.delay(product_id,ProductsToken)
            else:
                return render(request, 'order_detail.html', {'result':r.json().update({"detail": "Id not found."})} )

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            return HttpResponse(loader.render_to_string('503.html'), status=503) 
        
        logging.info(u"Delete product from order")
        r = redirect('agg1', user_id= user_id, order_id=order_id)
        if token != None:  
            r.set_cookie('ui_token',token)
        return r


class AggUserAllBuysView(CsrfExemptMixin,APIView):
    authentication_classes = []

    def get(self, request, user_id, format=None):
        if not has_access(request):
            if not refresh(request): 
                return HttpResponseRedirect(url_aggregator) 

        token = None
        if not has_access_ui(request):
            r = refresh_ui(request,user_id)
            if r:
                token = r    
            else:
                return HttpResponse(loader.render_to_string('403.html'), status=403)  
        
        try:
            r = requests.get(url_buys+"user/"+str(user_id)+"/",headers = make_header(BuysToken))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                if get_token(url_buys):
                    r = redirect('agg2', user_id= user_id)
                    if token != None: 
                        r.set_cookie('ui_token',token)
                    return r
            else:                                         
                return HttpResponse(loader.render_to_string( str(status_code)+'.html'), status=status_code)
        except requests.exceptions.RequestException:
            return HttpResponse(loader.render_to_string('503.html'), status=503)
        logging.info(u"Show orders")

        r = render(request, 'orders.html', {'result':r.json(object_pairs_hook=OrderedDict)})
        if token != None: 
            r.set_cookie('ui_token',token)
        return r
