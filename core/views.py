# Arquivo: core/views.py

from django.shortcuts import render, redirect
from .forms import UsuarioCreationForm

# Importações necessárias, incluindo 'logout'
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
# ---------------------------------------------

def index(request):
    """
    Esta view renderiza a página principal do site.
    """
    return render(request, 'index.html')

def reservas(request):
    """
    View para a página de reservas.
    """
    return render(request, 'reservas.html')

def contato(request):
    """
    View para a página de contato.
    """
    return render(request, 'contato.html')

def localizacao(request):
    """
    View para a página de localização.
    """
    return render(request, 'localizacao.html')

def criar_conta(request):
    """
    Renderiza e processa o formulário de criação de conta.
    """
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Adicionando mensagem de sucesso após criar a conta
            messages.success(request, 'Conta criada com sucesso! Agora você já pode fazer o login.')
            return redirect('entrar') # Redireciona para a página de login
    else:
        form = UsuarioCreationForm()
    
    context = {'form': form}
    return render(request, 'criar-conta.html', context)


def entrar(request):
    """
    Renderiza e processa o formulário de login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Mensagem de sucesso
                messages.success(request, f'Login realizado com sucesso! Bem-vindo(a), {user.first_name}.')
                return redirect('index')
            else:
                # Mensagem de erro (credenciais inválidas)
                messages.error(request, 'E-mail ou senha inválidos. Por favor, tente novamente.')
        else:
            # Mensagem de erro (formulário inválido)
            messages.error(request, 'Ocorreu um erro no formulário. Verifique os dados e tente novamente.')

    # Se a requisição for GET ou o formulário for inválido, renderiza a página de novo
    form = AuthenticationForm()
    return render(request, 'entrar.html', {'form': form})

# --- FUNÇÃO 'SAIR' ADICIONADA AQUI ---
def sair(request):
    """
    Encerra a sessão do usuário atual.
    """
    logout(request)
    messages.info(request, 'Você saiu da sua conta com segurança.')
    return redirect('index')