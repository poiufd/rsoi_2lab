from django.db import models

# Create your models here.
class Product(models.Model):
    model = models.CharField(max_length=25)
    year = models.IntegerField()
    country = models.CharField(max_length=35)
    count = models.PositiveIntegerField(default=1)

