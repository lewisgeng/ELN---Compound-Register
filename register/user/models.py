from django.db import models

# Create your models here.
class UsersInfo(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=1000)
    age=models.IntegerField(default=0)
    email=models.EmailField(default='')
    badge=models.IntegerField(default=0)
    phone_number=models.IntegerField(default=0)
    register_time = models.DateField(null=True,auto_now_add=True)
    ticket = models.CharField(max_length=1000,default='')