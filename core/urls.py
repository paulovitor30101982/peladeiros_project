from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reservas/', views.reservas, name='reservas'),
    path('contato/', views.contato, name='contato'),
    path('localizacao/', views.localizacao, name='localizacao'),
    path('criar-conta/', views.criar_conta, name='criar_conta'),
]