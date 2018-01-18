from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import requests.exceptions
import requests
from collections import OrderedDict
from django.http import HttpResponse, HttpResponseRedirect

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ag_service.settings')

app = Celery('ag_service')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


url_buys = 'http://localhost:8000/buys/'
url_products = 'http://localhost:8001/products/'
url_user = 'http://localhost:8002/user/'

ClientId = 'OdDr0vDribM42njMOQwmakhGC1vXaTogVyipMHjK'
ClientSecret = '0RoojuHswkIMfhPLt38yo2jIyjZzf9NZunMR8hcVm0e6h2nJrTDDM607ZNpRjZud5hjuMEo5NOR80ZG6e4dVkVDkJdLLZblf5B8mKBCBQVNfuZqi92CGzeibqofvQh3v'

def make_header(token):
    headers = {
                'Authorization': str(token),
                }   
    return headers 

def get_token(url):
    r = requests.get(url +"get_token/?clientId={}&clientSecret={}".format(ClientId,ClientSecret)) 
    if r.status_code == 200:         
        return r.json().get('Token') 
    else:
        return None

@app.task(bind=True, default_retry_delay=10)
def work_with_products(self, product_id,products_token):
    try:
        try:
            r = requests.get(url_products + str(product_id) + "/",headers = make_header(products_token))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                if get_token(url_products):
                    r = requests.get(url_products + str(product_id) + "/",headers = make_header(get_token(url_products)))
                else:                             
                    return HttpResponse(loader.render_to_string('403.html'), status=403)  
        r.raise_for_status()
        temp = r.json(object_pairs_hook=OrderedDict)
        c = temp.get('count')
        temp.update({'count': (c + 1)})
        try:
            r = requests.patch(url_products + str(product_id) + "/", temp,headers = make_header(products_token))
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                if get_token(url_products):
                    r = requests.get(url_products + str(product_id) + "/",headers = make_header(get_token(url_products)))
                else:                             
                    return HttpResponse(loader.render_to_string('403.html'), status=403)   
        r.raise_for_status()                      
        return HttpResponse(status=200)
       
    except requests.exceptions.RequestException as exc:
        raise self.retry(exc=exc, max_retries=100)
