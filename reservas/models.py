import uuid
from django.db import models
from django.conf import settings

class Espaco(models.Model):
    MODELO_COBRANCA_CHOICES = (('hora', 'Por Hora'), ('periodo', 'Por Período'))
    TIPO_CHOICES = (('campo', 'Campo'), ('churrasqueira', 'Churrasqueira'), ('quiosque', 'Quiosque'))
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='espacos_fotos/', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    capacidade = models.PositiveIntegerField()
    disponivel = models.BooleanField(default=True)
    modelo_de_cobranca = models.CharField(max_length=10, choices=MODELO_COBRANCA_CHOICES, default='hora')
    def __str__(self): return self.nome

class RegraPreco(models.Model):
    DIA_CHOICES = (
        (0, 'Segunda-feira'), (1, 'Terça-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'),
        (4, 'Sexta-feira'), (5, 'Sábado'), (6, 'Domingo'), (7, 'Dias de Semana (Seg-Sex)'),
        (8, 'Final de Semana (Sáb-Dom)'), (9, 'Segunda a Quinta (Seg-Qui)'),
        (10, 'Segundas, Quartas e Sextas (Seg-Qua-Sex)'), (11, 'Terças e Quintas (Ter-Qui)'),
    )
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='regras_preco_hora')
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    aplicar_em_feriados = models.BooleanField(default=False, help_text="Marque se este preço deve ser usado em feriados.")
    def __str__(self): return f"Preço/Hora para {self.espaco.nome} - {self.get_dia_semana_display()}"

class Periodo(models.Model):
    nome = models.CharField(max_length=50, help_text="Ex: Manhã, Tarde, Dia Inteiro")
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    def __str__(self): return f"{self.nome} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fim.strftime('%H:%M')})"

class PrecoPeriodo(models.Model):
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='regras_preco_periodo')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    dia_semana = models.IntegerField(choices=RegraPreco.DIA_CHOICES)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    aplicar_em_feriados = models.BooleanField(default=False, help_text="Marque se este preço deve ser usado em feriados.")
    def __str__(self): return f"Preço/Período para {self.espaco.nome} - {self.periodo.nome} ({self.get_dia_semana_display()})"

class Feriado(models.Model):
    data = models.DateField(unique=True)
    nome = models.CharField(max_length=100)
    def __str__(self): return f"{self.nome} ({self.data.strftime('%d/%m/%Y')})"

class Bloqueio(models.Model):
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='bloqueios_data')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self): return f"Bloqueio em {self.espaco.nome} de {self.data_inicio} até {self.data_fim}"

class BloqueioRecorrente(models.Model):
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE, related_name='bloqueios_recorrentes')
    dia_semana = models.IntegerField(choices=RegraPreco.DIA_CHOICES)
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    motivo = models.CharField(max_length=255, blank=True, null=True, help_text="Ex: Manutenção semanal, Aula fixa")
    def __str__(self): return f"Bloqueio Recorrente em {self.espaco.nome} - {self.get_dia_semana_display()} ({self.hora_inicio}-{self.hora_fim})"

class Reserva(models.Model):
    # --- STATUS ATUALIZADOS ---
    STATUS_CHOICES = (
        ('nao_lida', 'Não Lida'),
        ('em_tratamento', 'Em Tratamento'),
        ('tratado', 'Tratado'),
        ('cancelada_pelo_usuario', 'Cancelada pelo Usuário'), # NOVO STATUS
    )
    
    # ... (resto do seu modelo Reserva, sem alterações) ...
    codigo_reserva = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True)
    espaco = models.ForeignKey(Espaco, on_delete=models.PROTECT, related_name='reservas')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reservas_feitas')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    preco_final = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='nao_lida') # Aumentar max_length
    observacoes_admin = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Observações do Administrador",
        help_text="Anotações internas visíveis apenas para a administração."
    )
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        codigo = str(self.codigo_reserva)[:8] if self.codigo_reserva else "N/A"
        return f"Reserva {codigo} - {self.espaco.nome}"