from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    path('contacts/', views.contacts_list, name='contacts_list'),
    path('contacts/add/', views.add_contact, name='add_contact'),
    path('contacts/send/', views.send_money, name='send_money_anyone'),
    path('contacts/send/<int:friend_id>/', views.send_money, name='send_money'),

    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<int:message_id>/', views.message_detail, name='message_detail'),

    path('request/', views.request_money, name='request_money_anyone'),
    path('pay-request/<int:message_id>/', views.pay_request, name='pay_request'),

    path('gift/send/', views.send_gift, name='send_gift'),
    path('claim-gift/<int:message_id>/', views.claim_gift, name='claim_gift'),

    path('create-an-invoice', views.create_an_invoice, name='create_an_invoice'),
    path('transfer-to-bank', views.transfer_to_bank, name='transfer_to_bank'),

    path('resolution-centre', views.resolution_centre, name='resolution_centre'),
    path('report-transaction/<int:transaction_id>/', views.report_transaction, name='report_transaction'),

    path('goals', views.goals, name='goals'),

    path('history', views.history, name='history'),
    path('profile', views.profile, name='profile'),

    path('login', views.login_user, name='login_user'),
    path('register', views.register, name='register_user'),
    path('logout', views.logout_user, name='logout_user')
]
