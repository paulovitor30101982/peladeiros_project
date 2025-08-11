# Arquivo: usuarios/urls.py
from django.urls import path
from . import views

# Define um 'namespace' para este conjunto de URLs
app_name = 'usuarios'

urlpatterns = [
    path('criar-conta/', views.criar_conta, name='criar_conta'),
    path('entrar/', views.entrar, name='entrar'),
    path('sair/', views.sair, name='sair'),
    
    # --- NOVA ROTA PARA EDITAR O PERFIL ---
    path('minha-conta/', views.minha_conta, name='minha_conta'),
]