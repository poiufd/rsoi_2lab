from django.db import models

# Create your models here.
class Product(models.Model):
    model = models.CharField(max_length=25)
    year = models.CharField(max_length=30)
    country = models.CharField(max_length=35)