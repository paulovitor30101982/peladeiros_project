# Arquivo: core/views.py

from django.shortcuts import render, redirect
from .forms import UsuarioCreationForm
# Importações para a view de reservas
import json
from decimal import Decimal
from django.db.models import Min, Case, When, Value, DecimalField
from django.utils import timezone
from .models import Espaco, Bloqueio, BloqueioRecorrente, Periodo # Adicionei os modelos que faltavam

# Importações de autenticação
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
# ---------------------------------------------

def index(request):
    return render(request, 'index.html')

def reservas(request):
    """
    View para a página de reservas.
    Busca espaços, regras de preço e indisponibilidades (reservas/bloqueios).
    """
    # CORREÇÃO: A query agora busca o preço mínimo de ambas as tabelas (hora e período)
    # e seleciona o correto baseado no 'modelo_de_cobranca' do Espaco.
    espacos = Espaco.objects.filter(disponivel=True).annotate(
        min_preco_hora=Min('regras_preco_hora__preco'),
        min_preco_periodo=Min('regras_preco_periodo__preco')
    ).annotate(
        preco_minimo=Case(
            When(modelo_de_cobranca='hora', then='min_preco_hora'),
            When(modelo_de_cobranca='periodo', then='min_preco_periodo'),
            default=Value(None),
            output_field=DecimalField()
        )
    )

    # Coleta todas as indisponibilidades futuras
    agora = timezone.now()
    # Futuramente, adicionaremos as Reservas aqui
    bloqueios_futuros = Bloqueio.objects.filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')
    
    indisponibilidades = {}
    for item in list(bloqueios_futuros): 
        espaco_id = item['espaco_id']
        if espaco_id not in indisponibilidades:
            indisponibilidades[espaco_id] = {'datas_especificas': [], 'recorrentes': []}
        indisponibilidades[espaco_id]['datas_especificas'].append({
            'inicio': item['data_inicio'].isoformat(),
            'fim': item['data_fim'].isoformat(),
        })

    # Coleta os bloqueios recorrentes
    bloqueios_recorrentes = BloqueioRecorrente.objects.all()
    for bloqueio in bloqueios_recorrentes:
        espaco_id = bloqueio.espaco.id
        if espaco_id not in indisponibilidades:
            indisponibilidades[espaco_id] = {'datas_especificas': [], 'recorrentes': []}
        indisponibilidades[espaco_id]['recorrentes'].append({
            'dia_semana': bloqueio.dia_semana,
            'hora_inicio': bloqueio.hora_inicio.strftime('%H:%M:%S'),
            'hora_fim': bloqueio.hora_fim.strftime('%H:%M:%S'),
        })

    # Coleta as regras de preço por hora e por período
    regras_preco_hora_dict = {}
    regras_preco_periodo_dict = {}
    periodos = {p.id: {'nome': p.nome, 'inicio': p.hora_inicio, 'fim': p.hora_fim} for p in Periodo.objects.all()}

    for espaco in espacos:
        regras_preco_hora_dict[espaco.id] = list(espaco.regras_preco_hora.all().values())
        regras_preco_periodo_dict[espaco.id] = list(espaco.regras_preco_periodo.all().values())

    # Classe customizada para ensinar o JSON a converter tipos de dados do Python
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)
            if hasattr(obj, 'strftime'):
                return obj.strftime('%H:%M:%S')
            return super().default(obj)

    context = {
        'espacos': espacos,
        'regras_preco_hora_json': json.dumps(regras_preco_hora_dict, cls=CustomJSONEncoder),
        'regras_preco_periodo_json': json.dumps(regras_preco_periodo_dict, cls=CustomJSONEncoder),
        'periodos_json': json.dumps(periodos, cls=CustomJSONEncoder),
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