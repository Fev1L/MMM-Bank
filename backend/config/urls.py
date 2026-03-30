from django.contrib import admin
from django.urls import path

from main.views import (api_login, api_register, send_verification_code,
                        verify_code , check_username, create_account, api_dashboard_data,
                        api_logout, get_transactions)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/login/', api_login, name='api_login'),
    path('api/register/', api_register, name='api_register'),
    path('api/logout/', api_logout, name='api_logout'),

    path('api/send-code/', send_verification_code, name='send_verification_code'),
    path('api/verify-code/', verify_code, name='verify_code'),
    path('api/check-username/', check_username, name='check_username'),

    path('api/dashboard/', api_dashboard_data, name='api_dashboard_data'),
    path('api/accounts/create/', create_account, name='create_account'),
    path('api/transactions/', get_transactions, name='get_transactions')
]
