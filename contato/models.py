from django.db import models

class MensagemContato(models.Model):
    # --- NOVOS STATUS PARA O GERENCIAMENTO ---
    STATUS_CHOICES = (
        ('nao_lida', 'Não Lida'),
        ('em_tratamento', 'Em Tratamento'),
        ('lida', 'Lida'), # "Lida" agora significa concluído/resolvido
    )

    ASSUNTO_CHOICES = (
        ('duvida', 'Dúvida'),
        ('sugestao', 'Sugestão'),
        ('reclamacao', 'Reclamação'),
        ('reserva', 'Reservar para evento'),
        ('outro', 'Outro'),
    )
    
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    assunto = models.CharField(max_length=20, choices=ASSUNTO_CHOICES)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    
    # --- CAMPO 'lida' SUBSTITUÍDO POR 'status' ---
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='nao_lida' # Toda nova mensagem começa como "Não Lida"
    )

    # --- NOVO CAMPO PARA ANOTAÇÕES DO ADMIN ---
    anotacoes_admin = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Anotações Internas",
        help_text="Este campo é visível apenas para administradores."
    )

    def __str__(self):
        return f"Mensagem de {self.nome} sobre {self.get_assunto_display()}"

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ['status', '-data_envio']