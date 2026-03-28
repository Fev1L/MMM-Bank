from django.contrib import admin
from django.urls import path

from main.auth.views import api_login, api_register

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/login/', api_login, name='api_login'),
    path('api/register/', api_register, name='api_register'),
]
