from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='more'),

    path('casino/', views.casino_home, name='casino_home'),
    path('casino/slots', views.casino_slots, name='casino_slots'),
]