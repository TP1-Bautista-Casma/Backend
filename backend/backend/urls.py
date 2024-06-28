"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from api import views
from django.urls import path,re_path
from api.views import register,login,upload_image
#from api.views import UserCreateAPIView, UserLoginAPIView


urlpatterns = [
    path('admin/', admin.site.urls), 
    #path('api/register/', register.as_view(), name='register'),
    #path('api/login/', login.as_view(), name='login')
    re_path('login',views.login),
    re_path('register',views.register),
     path('upload/', upload_image, name='upload_image'),
    path('logout', views.logout, name='logout'), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
