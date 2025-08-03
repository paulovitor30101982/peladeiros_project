# Arquivo: core/views.py

from django.shortcuts import render, redirect
from .forms import UsuarioCreationForm
# Importações para a view de reservas
import json
from decimal import Decimal
from django.db.models import Min
from django.utils import timezone
from .models import Espaco, Bloqueio # Futuramente, adicione Reserva aqui

# Importações de autenticação
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
    Busca espaços, regras de preço e indisponibilidades (reservas/bloqueios).
    """
    espacos = Espaco.objects.filter(disponivel=True).annotate(
        preco_minimo=Min('regras_preco__preco')
    )

    # Coleta todos os bloqueios futuros
    agora = timezone.now()
    # Quando o modelo Reserva for criado, adicione-o aqui:
    # reservas_futuras = Reserva.objects.filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')
    bloqueios_futuros = Bloqueio.objects.filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')

    # Estrutura os horários indisponíveis para o JavaScript
    indisponibilidades = {}
    # Combine as listas quando o modelo Reserva existir: list(reservas_futuras) + list(bloqueios_futuros)
    for item in list(bloqueios_futuros):
        espaco_id = item['espaco_id']
        if espaco_id not in indisponibilidades:
            indisponibilidades[espaco_id] = []

        indisponibilidades[espaco_id].append({
            'inicio': item['data_inicio'].isoformat(),
            'fim': item['data_fim'].isoformat(),
        })

    # Coleta as regras de preço
    regras_preco_dict = {}
    for espaco in espacos:
        regras_preco_dict[espaco.id] = list(
            espaco.regras_preco.all().values('dia_semana', 'hora_inicio', 'hora_fim', 'preco')
        )

    # Classe customizada para ensinar o JSON a converter Decimais e Horários
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)
            if hasattr(obj, 'strftime'):
                return obj.strftime('%H:%M:%S')
            return super().default(obj)

    context = {
        'espacos': espacos,
        'regras_preco_json': json.dumps(regras_preco_dict, cls=CustomJSONEncoder),
        'indisponibilidades_json': json.dumps(indisponibilidades),
    }
    return render(request, 'reservas.html', context)


def contato(request):
    return render(request, 'contato.html')

def localizacao(request):
    return render(request, 'localizacao.html')

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