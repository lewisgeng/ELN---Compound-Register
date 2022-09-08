from django.db import models

# Create your models here.
class UsersInfo(models.Model):
    username = models.CharField(max_length=20)
    firstname = models.CharField(max_length=50,default='')
    lastname = models.CharField(max_length=50,default='')
    password = models.CharField(max_length=1000)
    age=models.IntegerField(default=0)
    email=models.EmailField(default='')
    badge=models.IntegerField(default=0)
    phone_number=models.IntegerField(default=0)
    register_time = models.DateField(null=True,auto_now_add=True)
    status = models.CharField(max_length=50,default='')
    role = models.CharField(max_length=50, default='')
    avatar_file_path = models.CharField(max_length=500,default='')