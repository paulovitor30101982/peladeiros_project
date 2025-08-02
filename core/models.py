from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    # Campos que já existiam...
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    
    # --- NOVO CAMPO "SEXO" ---
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)
    
    # Campos de endereço...
    cep = models.CharField(max_length=9, null=True, blank=True)
    logradouro = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    complemento = models.CharField(max_length=100, null=True, blank=True)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
