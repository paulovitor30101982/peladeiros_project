from django.shortcuts import render, redirect
from .forms import UsuarioCreationForm # Importe o formulário que criamos


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
        # Se o formulário foi enviado (método POST)
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save() # Salva o novo usuário no banco de dados
            # Futuramente, podemos adicionar uma mensagem de sucesso aqui.
            return redirect('index') # Redireciona para a página principal após o sucesso
    else:
        # Se o usuário apenas acessou a página (método GET)
        form = UsuarioCreationForm()
    
    context = {'form': form}
    return render(request, 'criar-conta.html', context)