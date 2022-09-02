from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
import pymysql
# Create your views here.
from .models import dbinfo
import cx_Oracle as cx


def database(request):
     if request.session.get('is_login'):
        html = '<center><p>数据库页面</p></br><a href = \'/index/\'>返回首页</a></center>'
        return HttpResponse(html)
     else:
         return redirect("/login/")
    #     if request.POST.get('dburl') != '' and request.POST.get('username') != '':
    #         database = request.POST.get('database')
    #         dburl = request.POST.get('dburl')
    #         username = request.POST.get('username')
    #         password = request.POST.get('password')
    #         hash_password = make_password(password)
    #         print(database,dburl,username,password)
    #         #before_insert_db = dbinfo.objects.all()
    #         #for item in before_insert_db:
    #          #   if item.dburl != dburl and item.username != username:
    #         if dburl != None and dbinfo.objects.filter(dburl=dburl).exists():
    #             db_current =  dbinfo.objects.get(dburl=dburl)
    #             if username == db_current.username:
    #                 return HttpResponse('已重复添加数据库信息')
    #         else:
    #             dbinfo.objects.create(dbtype=database, dburl=dburl, username=username, password=hash_password)
    #             dbinfo.save()
    #         after_insert_db = dbinfo.objects.all()
    #         db_list = []
    #         for item in after_insert_db:
    #             db_dict = {}
    #             db_dict['database'] = item.dbtype
    #             db_dict['dburl'] = item.dburl
    #             db_dict['username'] = item.username
    #             db_dict['password'] = item.password
    #             db_list.append(db_dict)
    #         return render(request,'database.html',{'db_list':db_list})
    #     else:
    #         ctx = {}
    #         ctx['aa'] = 'good'
    #         return render(request,'database.html', ctx)


