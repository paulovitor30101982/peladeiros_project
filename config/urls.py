from django.contrib import admin
from django.urls import path, include

# Imports para servir arquivos estáticos e de mídia em desenvolvimento
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Bloco para servir arquivos estáticos e de mídia durante o desenvolvimento
if settings.DEBUG:
    # A linha abaixo serve os arquivos de mídia (fotos dos espaços, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # A linha abaixo, que você já tinha, serve os arquivos estáticos (CSS, JS, etc.)
    # É bom mantê-la caso você tenha uma configuração específica.
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])