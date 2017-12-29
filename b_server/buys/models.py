from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Buy(models.Model):

    number = models.IntegerField(unique=True)
    user_id = models.IntegerField()
    products_id = ArrayField(models.IntegerField())
