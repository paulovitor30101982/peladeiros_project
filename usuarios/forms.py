# Arquivo: usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

# --------------------------------------------------------------------------
# Formulário para CRIAR uma nova conta de usuário
# --------------------------------------------------------------------------
class UsuarioCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Garante que o campo 'complemento' está incluído
        fields = (
            'username', 'first_name', 'sexo', 'email', 'cpf', 
            'data_nascimento', 'telefone', 'cep', 'logradouro', 'numero', 
            'complemento', 'bairro', 'cidade', 'estado'
        )
    
    first_name = forms.CharField(label="Nome Completo", required=True)
    sexo = forms.ChoiceField(choices=Usuario.SEXO_CHOICES, label="Sexo", required=True)
    email = forms.EmailField(label="E-mail", required=True)
    cpf = forms.CharField(label="CPF", required=True)
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        required=True,
        widget=forms.DateInput(),
        input_formats=['%d/%m/%Y'] 
    )
    telefone = forms.CharField(label="Telefone", required=True)
    cep = forms.CharField(label="CEP", required=True)
    logradouro = forms.CharField(label="Rua", required=True)
    numero = forms.CharField(label="Número", required=True)
    bairro = forms.CharField(label="Bairro", required=True)
    cidade = forms.CharField(label="Cidade", required=True)
    estado = forms.CharField(label="Estado", required=True)
    # Define o campo 'complemento' como não obrigatório
    complemento = forms.CharField(label="Complemento", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Seu nome completo', 'email': 'seuemail@exemplo.com',
            'cpf': '000.000.000-00', 'data_nascimento': 'dd/mm/aaaa',
            'telefone': '(00) 00000-0000', 'cep': '00000-000',
            'complemento': 'Apto / Bloco / Casa'
        }
        for field_name, text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = text
        
        self.fields['password1'].widget.attrs.update({'id': 'id_password1', 'autocomplete': 'new-password'})
        self.fields['password1'].label = "Senha"
        self.fields['password2'].widget.attrs.update({'id': 'id_password2', 'autocomplete': 'new-password'})
        self.fields['password2'].label = "Confirmar Senha"
        self.fields['first_name'].label = "Nome Completo"
        if 'username' in self.fields:
             self.fields['username'].widget = forms.HiddenInput()
        self.fields['data_nascimento'].widget.input_type = 'text'

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.username:
            user.username = user.email
        if commit:
            user.save()
        return user

# --------------------------------------------------------------------------
# Formulário para ATUALIZAR os dados de um usuário existente
# --------------------------------------------------------------------------
class AtualizacaoUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'first_name', 'email', 'sexo', 'cpf', 'data_nascimento', 'telefone', 
            'cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado'
        ]

    def __init__(self, *args, **kwargs):
        super(AtualizacaoUsuarioForm, self).__init__(*args, **kwargs)
        placeholders = {
            'first_name': 'Seu nome completo', 'email': 'seuemail@exemplo.com',
            'cpf': '000.000.000-00', 'data_nascimento': 'dd/mm/aaaa',
            'telefone': '(00) 00000-0000', 'cep': '00000-000',
            'complemento': 'Apto / Bloco / Casa'
        }
        for field_name, text in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = text
        
        self.fields['cpf'].widget.attrs['id'] = 'id_cpf'
        self.fields['telefone'].widget.attrs['id'] = 'id_telefone'
        self.fields['data_nascimento'].widget.attrs.update({'id': 'id_data_nascimento', 'type': 'text'})
        self.fields['cep'].widget.attrs['id'] = 'id_cep'

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        if commit:
            usuario.save()
        return usuario