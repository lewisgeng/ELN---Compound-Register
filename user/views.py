from django.shortcuts import render,redirect,HttpResponseRedirect
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators import csrf
from .models import UsersInfo
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.


def user_register(request):
    return render(request, 'user_register.html')

def register(request):
    reg_username = request.POST.get('reg_username')
    reg_password = request.POST.get('reg_password')
    list_user = UsersInfo.objects.all()
    for item in list_user:
        if reg_username == item.username and reg_password != '':
            return HttpResponse('用户名已被占用，请重新注册！')
        if reg_username == item.username and reg_password == '':
            return HttpResponse('用户名已被占用，且未输入密码！')
    if reg_username != '' and reg_password != '':
        hash_password = make_password(reg_password)
        info = UsersInfo(username=reg_username, password=hash_password)
        info.save()
        return HttpResponse('注册成功！')
    else:
        return HttpResponse('请填写完整的用户名和密码！')


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
                ctx = {}
                ctx['aa'] = '密码错误'
        else:
            ctx = {}
            ctx['aa'] = '用户不存在'
    else:
        ctx = {}
        ctx['aa'] = '请登录'
    return render(request, 'login.html', ctx)
    # return render(request, "login.html")

def logout(request):
    if request.session.get('is_login', True):
        request.session.flush()
        request.session.clear_expired()
        return redirect("/login/")


def index(request):
    if request.session.get('username'):
        ctx = {}
        ctx['aa'] = request.session.get('username')
        return render(request,'index.html',ctx)
    else:
        return redirect("/login/")

def documentation(request):
    if request.session.get('is_login'):
        return render(request,'documentation.html')
    else:
        return redirect("/login/")

def contact(request):
    if request.session.get('is_login'):
        return render(request,'contact.html')
    else:
        return redirect("/login/")
