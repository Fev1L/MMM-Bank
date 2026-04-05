from django.contrib import admin
from django.urls import path

from main.views import (api_login, api_register, send_verification_code,
                        verify_code , check_username, create_account, api_dashboard_data,
                        api_logout, get_transactions, api_send_money, api_send_gift,
                        api_request_money, api_claim_gift, api_confirm_payment_request,
                        api_exchange_money, api_delete_account)
from credits.views import api_credits, repay_credit
from deposits.views import api_piggy_bank, api_deposits_list, api_open_deposit, api_close_piggy

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
    path('api/transactions/', get_transactions, name='get_transactions'),

    path('api/send-money/', api_send_money, name='api_send_money'),
    path('api/request-money/', api_request_money, name='api_request_money'),
    path('api/send-gift/', api_send_gift, name='api_send_gift'),
    path('api/claim-gift/<uuid:request_id>/', api_claim_gift, name='api_claim_gift'),
    path('api/api-confirm-payment-request/<uuid:request_id>/', api_confirm_payment_request, name='api_confirm_payment_request'),

    path('api/exchange/', api_exchange_money, name='api_exchange_money'),
    path('api/accounts/<str:currency_code>/delete/', api_delete_account, name='api_delete_account'),

    path('api/credits/', api_credits, name='api_credits'),
    path('api/repay-credit/', repay_credit, name='repay_credit'),

    path('api/piggy-bank/', api_piggy_bank, name='api_piggy_bank'),
    path('api/piggy-bank/<int:piggy_id>/close/', api_close_piggy, name='api_close_piggy'),
    path('api/deposits/', api_deposits_list, name='api_deposits_list'),
    path('api/deposits/open/', api_open_deposit, name='api_open_deposit')
]
