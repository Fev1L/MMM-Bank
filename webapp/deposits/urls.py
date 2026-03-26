from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='deposit'),
    path('open/', views.open_deposit, name='open_deposit'),
    path('piggy-bank/', views.piggy_bank, name='piggy_bank'),
    path('bonds/', views.buy_bonds, name='buy_bonds'),
]