# contato/models.py
from django.db import models

class MensagemContato(models.Model):
    # --- OPÇÕES DEFINIDAS AQUI ---
    ASSUNTO_CHOICES = [
        ('Elogio', 'Elogio'),
        ('Sugestão', 'Sugestão'),
        ('Reclamação', 'Reclamação'),
        ('Reservar para evento', 'Reservar para evento'),
    ]

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True, null=True)
    # --- CAMPO 'ASSUNTO' ATUALIZADO PARA USAR AS OPÇÕES ---
    assunto = models.CharField(max_length=150, choices=ASSUNTO_CHOICES)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)

    def __str__(self):
        return f'Mensagem de {self.nome} - {self.get_assunto_display()}'

    class Meta:
        verbose_name = "Mensagem de Contato"
        verbose_name_plural = "Mensagens de Contato"
        ordering = ['-data_envio']