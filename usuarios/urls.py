from django.urls import path
from . import views

urlpatterns = [
    path('criar-conta/', views.criar_conta, name='criar_conta'),
    path('entrar/', views.entrar, name='entrar'),
    path('sair/', views.sair, name='sair'),
    path('minhas-reservas/', views.minhas_reservas, name='minhas_reservas'),
    
    # --- NOVA ROTA PARA CANCELAR UMA RESERVA ---
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
]