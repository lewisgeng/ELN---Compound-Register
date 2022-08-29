"""genglv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from user import views
import user.views as user_view
import mol_registration.views as mol_registration_view
import database.views as database_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('contact', views.contact),

    #app-user相关的url
    path('login/', views.login),
    path('user_register', views.user_register),
    path('register_result', views.register),
    path('logout', views.logout),

    #app-mol_register相关的url
    path('registration/', mol_registration_view.registration),
    path('reg_result/', mol_registration_view.reg_result),
    path('search/', mol_registration_view.search),
    path('compoundlist/', mol_registration_view.compoundlist),

    #app-database相关的url
    path('database/', database_view.database),

]
