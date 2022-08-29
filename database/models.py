from django.db import models

# Create your models here.
class dbinfo(models.Model):
    dbtype = models.CharField(max_length=30)
    dburl = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=1000)
    schema = models.CharField(max_length=50)
    table = models.CharField(max_length=50)