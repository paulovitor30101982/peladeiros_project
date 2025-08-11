# Arquivo: contato/urls.py
from django.urls import path
from . import views

app_name = 'contato'

urlpatterns = [
    # Rota da página pública de contato
    path('', views.contato, name='contato'),
    
    # --- NOVAS ROTAS DA ÁREA RESTRITA ---
    # Rota para a lista de mensagens
    path('mensagens/', views.lista_mensagens, name='lista_mensagens'),
    
    # Rota para ver o detalhe de uma mensagem específica
    path('mensagens/<int:mensagem_id>/', views.detalhe_mensagem, name='detalhe_mensagem'),
    
    # Rota para a ação de marcar como lida
    path('mensagens/<int:mensagem_id>/marcar-lida/', views.marcar_como_lida, name='marcar_como_lida'),
    
    # Rota para a ação de apagar a mensagem
    path('mensagens/<int:mensagem_id>/deletar/', views.deletar_mensagem, name='deletar_mensagem'),
]