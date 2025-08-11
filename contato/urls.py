# contato/urls.py
from django.urls import path
from . import views

app_name = 'contato'

urlpatterns = [
    path('', views.contato, name='contato'),
    path('mensagens/', views.lista_mensagens, name='lista_mensagens'),
]