from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    path('contacts/', views.contacts_list, name='contacts_list'),
    path('contacts/add/', views.add_contact, name='add_contact'),
    path('contacts/send/<int:friend_id>/', views.send_money, name='send_money'),
    path('contacts/send/', views.send_money_anyone, name='send_money_anyone'),

    path('history', views.history, name='history'),
    path('profile', views.profile, name='profile'),

    path('login', views.login_user, name='login_user'),
    path('register', views.register, name='register_user'),
    path('logout', views.logout_user, name='logout_user')
]
