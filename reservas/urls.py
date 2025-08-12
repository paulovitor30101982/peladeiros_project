# Arquivo: reservas/urls.py
# NENHUMA ALTERAÇÃO NECESSÁRIA.

from django.urls import path
from . import views

# Define um 'app_name' para evitar conflito de nomes de URL com outras apps
app_name = 'reservas'

urlpatterns = [
    path('reservas/', views.reservas, name='reservas'),
    path('finalizar-reserva/', views.finalizar_reserva, name='finalizar_reserva'),

    # --- NOVAS URLS ---
    # URL para a página que lista as reservas do usuário
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),

    # URL para a ação de cancelar uma reserva específica
    # <int:reserva_id> captura o ID da reserva a partir da URL
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
]