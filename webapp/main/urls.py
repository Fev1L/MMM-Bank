from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('', views.index, name='home'),
    path('', views.index, name='home'),
    path('more', views.more, name='more'),

    path('login', views.login_user, name='login_user'),
    path('register', views.register, name='register_user'),
    path('logout', views.logout_user, name='logout_user')
]
