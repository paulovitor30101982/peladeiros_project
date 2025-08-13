# contato/forms.py
from django import forms
from .models import MensagemContato

class ContatoForm(forms.ModelForm):
    class Meta:
        model = MensagemContato
        fields = ['nome', 'email', 'telefone', 'assunto', 'mensagem']
        # Removemos os widgets daqui para os definir no __init__
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define os placeholders para cada campo
        placeholders = {
            'nome': 'O seu nome completo',
            'email': 'O seu melhor e-mail',
            'telefone': 'O seu número de telefone',
            'mensagem': 'Escreva a sua mensagem aqui...',
        }

        # Adiciona os placeholders e a classe CSS a cada campo
        for field_name, text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = text
        
        # Adiciona uma opção inicial "Selecione..." ao campo de assunto
        self.fields['assunto'].empty_label = "Selecione o motivo do contato..."

        # Garante que todos os campos tenham a classe 'form-control' para estilização
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})