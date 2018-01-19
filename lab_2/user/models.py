from django.db import models

# Create your models here.
class User(models.Model):
    login = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=30)
    name = models.CharField(max_length=35)

class UserUiAccManager(models.Manager):
    def create_new(self, user_id, token, res_time):
        obj = self.create(user_id = user_id,token = token, res_time = res_time)
        return obj

class UserUiAcc(models.Model):
	user_id = models.IntegerField(unique=True)
	token = models.CharField(max_length=45)
	res_time = models.DecimalField(max_digits=30, decimal_places=15)

	objects = UserUiAccManager()	
