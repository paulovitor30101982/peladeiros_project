# Arquivo: main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('contato/', views.contato, name='contato'),
    path('localizacao/', views.localizacao, name='localizacao'),
]