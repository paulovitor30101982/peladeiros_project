from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    # --- URLs para USUÁRIOS FINAIS (já existentes) ---
    path('reservas/', views.reservas, name='reservas'),
    path('finalizar-reserva/', views.finalizar_reserva, name='finalizar_reserva'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    
    
    # --- NOVAS URLs PARA O PAINEL DO ADMINISTRADOR ---
    # Lista todas as reservas para o admin gerenciar
    path('gerenciar/', views.gerenciar_reservas, name='gerenciar_reservas'),

    # Página de detalhes para o admin editar uma reserva específica
    path('gerenciar/<int:reserva_id>/', views.detalhe_reserva_admin, name='detalhe_reserva_admin'),
]