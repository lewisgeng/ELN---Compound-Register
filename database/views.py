from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import pymysql
# Create your views here.
from .models import dbinfo
import cx_Oracle as cx


def database(request):
     if request.session.get('is_login'):
         db = {}
         db['msg'] = '这是来自database的数据'
         return render(request, "index.html", db)
     else:
         return redirect("/login/")



