from django.utils.timezone import make_aware
from django.shortcuts import render, get_object_or_404, redirect
import json
from decimal import Decimal
from django.db.models import Min, Case, When, Value, DecimalField
from django.utils import timezone
from .models import Espaco, Bloqueio, BloqueioRecorrente, Periodo, Reserva, Feriado
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta
from django.contrib import messages
from .forms import ReservaAdminForm

monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
    'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

def is_staff_member(user):
    return user.is_staff

def reservas(request):
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
    
    # --- CORREÇÃO 1: Garante que a checagem de indisponibilidade considera todos os status de cancelamento ---
    status_cancelados = ['cancelada', 'cancelada_pelo_usuario']
    reservas_futuras = Reserva.objects.exclude(status__in=status_cancelados).filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')
    
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
    feriados = {f.data.isoformat(): f.nome for f in Feriado.objects.all()}
    for espaco in espacos:
        regras_preco_hora_dict[espaco.id] = list(espaco.regras_preco_hora.all().values())
        regras_preco_periodo_dict[espaco.id] = list(espaco.regras_preco_periodo.all().values())
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal): return str(obj)
            if hasattr(obj, 'strftime'): return obj.strftime('%H:%M:%S')
            return super().default(obj)
    context = {
        'espacos': espacos,
        'regras_preco_hora_json': json.dumps(regras_preco_hora_dict, cls=CustomJSONEncoder),
        'regras_preco_periodo_json': json.dumps(regras_preco_periodo_dict, cls=CustomJSONEncoder),
        'periodos_json': json.dumps(periodos, cls=CustomJSONEncoder),
        'indisponibilidades_json': json.dumps(indisponibilidades),
        'feriados_json': json.dumps(feriados),
    }
    return render(request, 'reservas.html', context)


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
                    data_inicio_naive = datetime.strptime(data_reserva_str, '%Y-%m-%d %H:%M')
                    data_fim_naive = data_inicio_naive + timedelta(hours=1)
                else:
                    periodo_nome = item['time'].split(' (')[0].strip()
                    periodo = Periodo.objects.get(nome=periodo_nome)
                    data_reserva_str_inicio = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_inicio}"
                    data_reserva_str_fim = f"{item['year']}-{month_map[item['month']]}-{item['day']} {periodo.hora_fim}"
                    data_inicio_naive = datetime.strptime(data_reserva_str_inicio, '%Y-%m-%d %H:%M:%S')
                    data_fim_naive = datetime.strptime(data_reserva_str_fim, '%Y-%m-%d %H:%M:%S')

                data_inicio = make_aware(data_inicio_naive)
                data_fim = make_aware(data_fim_naive)
                
                # --- CORREÇÃO 2: Garante que a checagem de conflitos considera todos os status de cancelamento ---
                status_cancelados = ['cancelada', 'cancelada_pelo_usuario']
                conflitos = Reserva.objects.filter(
                    espaco=espaco,
                    data_inicio__lt=data_fim,
                    data_fim__gt=data_inicio
                ).exclude(status__in=status_cancelados)

                if conflitos.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f"O horário para {item['item']} no dia {item['day']}/{month_map[item['month']]} já foi reservado. Por favor, atualize a página e tente novamente."
                    }, status=409)

                Reserva.objects.create(
                    espaco=espaco,
                    usuario=request.user,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    preco_final=item['price'],
                    status='nao_lida'
                )
            
            return JsonResponse({'status': 'success', 'message': 'Sua reserva foi enviada para confirmação!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@login_required(login_url='/entrar/')
def minhas_reservas(request):
    """
    Busca as reservas do usuário logado e as separa em abas:
    Próximas, Utilizadas e Canceladas.
    """
    agora = timezone.now()
    reservas_usuario = Reserva.objects.filter(usuario=request.user).order_by('-data_inicio')

    # --- CORREÇÃO 3: Lógica principal ajustada para lidar com múltiplos status de cancelamento ---
    status_cancelados = ['cancelada_pelo_usuario', 'cancelada']

    proximas = reservas_usuario.exclude(status__in=status_cancelados).filter(data_fim__gte=agora)
    utilizadas = reservas_usuario.exclude(status__in=status_cancelados).filter(data_fim__lt=agora)
    canceladas = reservas_usuario.filter(status__in=status_cancelados)

    context = {
        'proximas': proximas,
        'utilizadas': utilizadas,
        'canceladas': canceladas,
    }
    return render(request, 'minhas_reservas.html', context)


@login_required(login_url='/entrar/')
@require_POST
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    agora = timezone.now()
    if reserva.data_inicio > agora:
        reserva.status = 'cancelada_pelo_usuario'
        reserva.save()
        messages.success(request, 'Sua reserva foi cancelada com sucesso.')
    else:
        messages.error(request, 'Não é possível cancelar uma reserva que já ocorreu.')
    return redirect('reservas:minhas_reservas')


# ----- VIEWS PARA O PAINEL DO ADMINISTRADOR -----

@user_passes_test(is_staff_member)
def gerenciar_reservas(request):
    reservas_list = Reserva.objects.all().order_by('status', '-data_criacao')
    context = {
        'reservas': reservas_list
    }
    return render(request, 'gerenciar_reservas.html', context)


@user_passes_test(is_staff_member)
def detalhe_reserva_admin(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        form = ReservaAdminForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'A reserva foi atualizada com sucesso!')
            return redirect('reservas:detalhe_reserva_admin', reserva_id=reserva.id)
    else:
        form = ReservaAdminForm(instance=reserva)
    context = {
        'reserva': reserva,
        'form': form,
    }
    return render(request, 'detalhe_reserva_admin.html', context)