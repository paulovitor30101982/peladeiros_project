from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Aqui definimos os campos que aparecerão no formulário
        fields = ('username', 'first_name', 'last_name', 'email', 'cpf', 'data_nascimento', 'telefone')