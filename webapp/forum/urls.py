from django.urls import path
from . import views # from current folder import the neighbour file views for views methods usage

urlpatterns = [
    path('', views.index),
    path('frequent_questions', views.frequent_questions)
]
 