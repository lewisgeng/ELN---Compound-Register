import os
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators import csrf
from django.contrib.auth.hashers import make_password, check_password
import datetime
from time import strftime
from .models import UsersInfo
import random
import string


def user_admin(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if request.method == 'POST':
            reg_username = request.POST.get('reg_username')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email')
            role = request.POST.get('role')
            avatar_default = '/static/avatar/default.png'
            avatar_file_path = avatar_default
            if UsersInfo.objects.filter(username=reg_username).exists():
                message = '用户名已存在，请重新输入！'
            elif password1 != password2:
                message = '两次密码不一致！！'
            else:
                hash_password = make_password(password1)
                info = UsersInfo(username=reg_username, password=hash_password,firstname=firstname,lastname=lastname,email=email,role=role,avatar_file_path=avatar_file_path)
                info.save()
                message = '添加用户成功！'
            user_list = UsersInfo.objects.all()
            user_show = []
            for user in user_list:
                user_dict = {}
                user_dict['default_id'] = user.id
                user_dict['username'] = user.username
                user_dict['firstname'] = user.firstname
                user_dict['lastname'] = user.lastname
                user_dict['email'] = user.email
                user_dict['role'] = user.role
                user_show.append(user_dict)
            return render(request, 'user_admin.html', locals())
        else:
            user_list = UsersInfo.objects.all()
            user_show = []
            for user in user_list:
                user_dict = {}
                user_dict['default_id'] = user.id
                user_dict['username'] = user.username
                user_dict['firstname'] = user.firstname
                user_dict['lastname'] = user.lastname
                user_dict['email'] = user.email
                user_dict['role'] = user.role
                user_show.append(user_dict)
            return render(request, 'user_admin.html', locals())
    else:
        return redirect("/login/")
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if UsersInfo.objects.filter(username=username).exists():
            user = UsersInfo.objects.get(username=username)
            if check_password(password, user.password):
                request.session['is_login'] = True
                request.session['userid'] = user.id
                request.session['username'] = user.username
                return redirect('/index/')
            if not check_password(password, user.password):
                message = '密码错误'
        else:
            message = '用户不存在'
    else:
        message = ''
    return render(request, 'login.html', locals())

def logout(request):
    if request.session.get('is_login', True):
        request.session.flush()
        request.session.clear_expired()
        return redirect("/login/")

def profile(request):
    if request.session.get('is_login'):
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username = username)
        if request.method == 'POST':
            new_email = request.POST.get('email')
            oldpassword = request.POST.get('oldpassword')
            newpassword1 = request.POST.get('newpassword1')
            newpassword2 = request.POST.get('newpassword2')
            if check_password(oldpassword, user_info.password):
                if newpassword1 == newpassword2:
                    user_info.email = new_email
                    user_info.password = make_password(newpassword1)
                    user_info.save()
                    message = '密码更新成功！'
                else:
                    message = '新密码验证失败，请重新输入!'
            else:
                message = '原始密码输入错误，请重新输入!'
            return render(request, 'profile.html', locals())
        return render(request, 'profile.html', locals())
    else:
        return redirect("/login/")
#
def avatar(request):
    if request.method == 'GET':
        #return render(request,'upload.html')
        return HttpResponse("None")
    if request.method == 'POST':
        file_content = request.FILES.get("avatar_file", None)
        username = request.session.get('username')
        user_info = UsersInfo.objects.get(username=username)
        if not file_content:
            return HttpResponse("没有上传内容")
        else:
            random_name = ''.join(random.sample(string.ascii_letters + string.digits, 50))
            filename = random_name +'.'+ file_content.name.split('.')[-1]
            file_upload = os.path.join('./register/template/static/avatar/', filename)
            #获取上传文件的文件名，并将其存储到指定位置
            print(file_upload)
            storage = open(file_upload,'wb+')       #打开存储文件
            for chunk in file_content.chunks():       #分块写入文件
                storage.write(chunk)
            storage.close()
            file_upload = file_upload.replace('./register/template','')
            print(file_upload)
            user_info.avatar_file_path = file_upload
            user_info.save()
            return redirect('/profile/')
    else:
        return redirect('/profile/')




