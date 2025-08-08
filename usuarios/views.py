# Arquivo: usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .forms import UsuarioCreationForm
from reservas.models import Reserva # Importa o modelo Reserva da app 'reservas'

@login_required(login_url='/entrar/')
def minhas_reservas(request):
    agora = timezone.now()
    reservas_proximas = Reserva.objects.filter(
        usuario=request.user, status='confirmada', data_inicio__gte=agora
    ).order_by('data_inicio')
    reservas_historico = Reserva.objects.filter(
        usuario=request.user, status='confirmada', data_inicio__lt=agora
    ).order_by('-data_inicio')
    reservas_canceladas = Reserva.objects.filter(
        usuario=request.user, status='cancelada'
    ).order_by('-data_criacao')
    
    context = {
        'proximas': reservas_proximas,
        'historico': reservas_historico,
        'canceladas': reservas_canceladas,
    }
    return render(request, 'minhas_reservas.html', context)

def criar_conta(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Você já pode fazer o login.')
            return redirect('entrar')
    else:
        form = UsuarioCreationForm()
    return render(request, 'criar-conta.html', {'form': form})

def entrar(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Login realizado com sucesso! Bem-vindo(a), {user.first_name}.')
                return redirect('index')
            else:
                messages.error(request, 'E-mail ou senha inválidos. Por favor, tente novamente.')
    else:
        form = AuthenticationForm()
    return render(request, 'entrar.html', {'form': form})

def sair(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta com segurança.')
    return redirect('index')

@login_required(login_url='/entrar/')
def cancelar_reserva(request, reserva_id):
    """
    Muda o status de uma reserva específica para 'cancelada'.
    """
    # Garante que a reserva existe e pertence ao usuário que está a fazer o pedido
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    if request.method == 'POST':
        # Altera o status para 'cancelada'
        reserva.status = 'cancelada'
        reserva.save()
        
        # Envia uma resposta de sucesso para o JavaScript
        return JsonResponse({'status': 'success', 'message': 'Reserva cancelada com sucesso.'})

    # Se o método não for POST, retorna um erro
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)
