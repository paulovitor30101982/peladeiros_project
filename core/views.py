# Arquivo: core/views.py

from django.shortcuts import render, redirect
from .forms import UsuarioCreationForm
import json
from decimal import Decimal
from django.db.models import Min, Case, When, Value, DecimalField
from django.utils import timezone
from .models import Espaco, Bloqueio, BloqueioRecorrente, Periodo, Reserva 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
# ---------------------------------------------

# Lista de meses para o backend entender os dados do carrinho
monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

def index(request):
    return render(request, 'index.html')

def reservas(request):
    # ... (esta view permanece a mesma, sem alterações)
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
    agora = timezone.now()
    reservas_futuras = Reserva.objects.filter(data_fim__gte=agora, status='confirmada').values('espaco_id', 'data_inicio', 'data_fim')
    bloqueios_futuros = Bloqueio.objects.filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')
    indisponibilidades = {}
    for item in list(reservas_futuras) + list(bloqueios_futuros): 
        espaco_id = item['espaco_id']
        if espaco_id not in indisponibilidades:
            indisponibilidades[espaco_id] = {'datas_especificas': [], 'recorrentes': []}
        indisponibilidades[espaco_id]['datas_especificas'].append({
            'inicio': item['data_inicio'].isoformat(),
            'fim': item['data_fim'].isoformat(),
        })
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
    regras_preco_hora_dict = {}
    regras_preco_periodo_dict = {}
    periodos = {p.id: {'nome': p.nome, 'inicio': p.hora_inicio, 'fim': p.hora_fim} for p in Periodo.objects.all()}
    for espaco in espacos:
        regras_preco_hora_dict[espaco.id] = list(espaco.regras_preco_hora.all().values())
        regras_preco_periodo_dict[espaco.id] = list(espaco.regras_preco_periodo.all().values())
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

@login_required(login_url='/entrar/')
@csrf_exempt
def finalizar_reserva(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart_items = data.get('cart_items')
            month_map = {name: index + 1 for index, name in enumerate(monthNames)}

            if not cart_items:
                return JsonResponse({'status': 'error', 'message': 'O carrinho está vazio.'}, status=400)

            for item in cart_items:
                espaco = Espaco.objects.get(id=item['espacoId'])
                
                if espaco.modelo_de_cobranca == 'hora':
                    data_reserva_str = f"{item['year']}-{month_map[item['month']]}-{item['day']} {item['time']}"
                    data_inicio = datetime.strptime(data_reserva_str, '%Y-%m-%d %H:%M')
                    data_fim = data_inicio + timedelta(hours=1)
                else:
                    # --- CORREÇÃO APLICADA AQUI ---
                    # Extrai o nome completo do período antes do parêntese
                    periodo_nome = item['time'].split(' (')[0].strip()
                    periodo = Periodo.objects.get(nome=periodo_nome)
                    data_reserva_str_inicio = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_inicio}"
                    data_reserva_str_fim = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_fim}"
                    data_inicio = datetime.strptime(data_reserva_str_inicio, '%Y-%m-%d %H:%M:%S')
                    data_fim = datetime.strptime(data_reserva_str_fim, '%Y-%m-%d %H:%M:%S')

                conflitos = Reserva.objects.filter(
                    espaco=espaco,
                    data_inicio__lt=data_fim,
                    data_fim__gt=data_inicio,
                    status='confirmada'
                )
                if conflitos.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f"O horário para {item['item']} no dia {item['day']}/{month_map[item['month']]} já foi reservado. Por favor, atualize a página e tente novamente."
                    }, status=409)

            for item in cart_items:
                espaco = Espaco.objects.get(id=item['espacoId'])
                if espaco.modelo_de_cobranca == 'hora':
                    data_reserva_str = f"{item['year']}-{month_map[item['month']]}-{item['day']} {item['time']}"
                    data_inicio = datetime.strptime(data_reserva_str, '%Y-%m-%d %H:%M')
                    data_fim = data_inicio + timedelta(hours=1)
                else:
                    periodo_nome = item['time'].split(' (')[0].strip()
                    periodo = Periodo.objects.get(nome=periodo_nome)
                    data_reserva_str_inicio = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_inicio}"
                    data_reserva_str_fim = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_fim}"
                    data_inicio = datetime.strptime(data_reserva_str_inicio, '%Y-%m-%d %H:%M:%S')
                    data_fim = datetime.strptime(data_reserva_str_fim, '%Y-%m-%d %H:%M:%S')
                
                Reserva.objects.create(
                    espaco=espaco,
                    usuario=request.user,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    preco_final=item['price'],
                    status='confirmada'
                )

            return JsonResponse({'status': 'success', 'message': 'Sua reserva foi confirmada com sucesso!'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno: {str(e)}'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)