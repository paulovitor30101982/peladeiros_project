# Arquivo: config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ROTA CORRIGIDA (MOVIDA PARA CIMA) ---
    # Colocamos a rota mais específica primeiro. Agora, quando aceder a /contato/,
    # o Django irá encontrar esta rota e usar a sua nova aplicação 'contato' imediatamente.
    path('contato/', include('contato.urls')), 
    
    # As outras rotas podem permanecer como estavam.
    path('', include('main.urls')), 
    path('', include('usuarios.urls')), 
    path('', include('reservas.urls')), 
]

# (O bloco para servir arquivos de mídia em desenvolvimento permanece o mesmo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)