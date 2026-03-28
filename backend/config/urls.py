from django.contrib import admin
from django.urls import path

from main.views import api_login, api_register, send_verification_code, verify_code

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/login/', api_login, name='api_login'),
    path('api/register/', api_register, name='api_register'),

    path('api/send-code/', send_verification_code, name='send_verification_code'),
    path('api/verify-code/', verify_code, name='verify_code'),
]
