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

# --- NOVOS MODELOS PARA O SISTEMA DE RESERVAS ---

class Espaco(models.Model):
    TIPO_CHOICES = (
        ('campo', 'Campo'),
        ('churrasqueira', 'Churrasqueira'),
        ('quiosque', 'Quiosque'),
    )

    nome = models.CharField(max_length=100, help_text="Ex: Campo Society 1")
    descricao = models.TextField(blank=True, null=True, help_text="Detalhes sobre o espaço.")
    foto = models.ImageField(upload_to='espacos_fotos/', blank=True, null=True, help_text="Foto de destaque do espaço.")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo de espaço.")
    capacidade = models.PositiveIntegerField(help_text="Número máximo de pessoas que o espaço comporta.")
    disponivel = models.BooleanField(default=True, help_text="Marque se o espaço está disponível para novas reservas.")

    def __str__(self):
        return self.nome

class RegraPreco(models.Model):
    DIA_SEMANA_CHOICES = (
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )

    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='regras_preco')
    dia_semana = models.IntegerField(choices=DIA_SEMANA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    preco = models.DecimalField(max_digits=8, decimal_places=2, help_text="Preço por hora neste horário específico.")

    def __str__(self):
        return f"Regra para {self.espaco.nome} - {self.get_dia_semana_display()} ({self.hora_inicio}-{self.hora_fim})"

class Bloqueio(models.Model):
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='bloqueios')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Manutenção, Evento fechado.")

    def __str__(self):
        return f"Bloqueio em {self.espaco.nome} de {self.data_inicio} até {self.data_fim}"
