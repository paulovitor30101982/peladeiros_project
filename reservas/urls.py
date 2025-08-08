# Arquivo: reservas/urls.py (NOVO ARQUIVO)

from django.urls import path
from . import views

urlpatterns = [
    path('reservas/', views.reservas, name='reservas'),
    path('finalizar-reserva/', views.finalizar_reserva, name='finalizar_reserva'),
]