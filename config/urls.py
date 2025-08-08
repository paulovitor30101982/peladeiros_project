# Arquivo: config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- ROTAS ATUALIZADAS ---
    # Inclui as URLs da app 'main' (para home, contato, etc.)
    path('', include('main.urls')), 
    
    # Inclui as URLs da app 'usuarios' (para login, cadastro, etc.)
    path('', include('usuarios.urls')), 
    
    # Inclui as URLs da app 'reservas' (para a pág. de reservas e finalização)
    path('', include('reservas.urls')), 
]

# (O bloco para servir arquivos de mídia em desenvolvimento permanece o mesmo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])