from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='credits'),
    path('pay_extra', views.pay_extra, name='pay_extra'),
    path('avaible_loans', views.avaible_loans, name='avaible_loans'),
]