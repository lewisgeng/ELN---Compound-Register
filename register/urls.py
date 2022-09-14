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
import user.views as user_view
import mol_registration.views as mol_registration_view

urlpatterns = [
    path('admin/', admin.site.urls),


    #app-user相关的url
    path('login/', user_view.login),
    path('logout', user_view.logout),
    path('user_admin/', user_view.user_admin),
    path('profile/', user_view.profile),
    path('profile/avatar', user_view.avatar),


    #app-mol_register相关的url
    path('index/', mol_registration_view.index),
    path('registration/', mol_registration_view.registration),
    path('reg_result/', mol_registration_view.reg_result),
    # path('search/', mol_registration_view.search),
    # path('search_result/', mol_registration_view.search_result),
    path('compoundlist/', mol_registration_view.compoundlist),
    path('reagentlist/', mol_registration_view.reagentlist),
    path('delete_compound/', mol_registration_view.delete_compound),
    path('confirm_delete_compound/', mol_registration_view.confirm_delete_compound),
    path('edit_compound/', mol_registration_view.edit_compound),
    path('upload/', mol_registration_view.upload),
    path('custome_fields/', mol_registration_view.custome_fields)
    #app-database相关的url
    #path('index/', database_view.database),

]
