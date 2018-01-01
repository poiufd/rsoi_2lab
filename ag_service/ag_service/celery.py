from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import requests.exceptions
import requests
from collections import OrderedDict

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


@app.task(bind=True, default_retry_delay=10)
def work_with_products(self, product_id):
    try:
        r = requests.get(url_products + str(product_id) + "/")
        r.raise_for_status()
        temp = r.json(object_pairs_hook=OrderedDict)
        c = temp.get('count')
        temp.update({'count': (c + 1)})
        r = requests.patch(url_products + str(product_id) + "/", temp)
        r.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise self.retry(exc=exc, max_retries=100)