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
from .forms import ReservaAdminForm # Importa o novo formulário

monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
    'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

# Função auxiliar para checar se o usuário é do time de administração (staff)
def is_staff_member(user):
    return user.is_staff

# ----- VIEWS PÚBLICAS E DE USUÁRIOS -----

def reservas(request):
    # (Nenhuma alteração necessária nesta view)
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
    reservas_futuras = Reserva.objects.exclude(status='cancelada').filter(data_fim__gte=agora).values('espaco_id', 'data_inicio', 'data_fim')
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
    # (Alteração principal: status da nova reserva)
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
                
                conflitos = Reserva.objects.filter(
                    espaco=espaco,
                    data_inicio__lt=data_fim,
                    data_fim__gt=data_inicio
                ).exclude(status='cancelada')
                if conflitos.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f"O horário para {item['item']} no dia {item['day']}/{month_map[item['month']]} já foi reservado. Por favor, atualize a página e tente novamente."
                    }, status=409)

                # --- MUDANÇA AQUI: Nova reserva entra como "Não Lida" ---
                Reserva.objects.create(
                    espaco=espaco,
                    usuario=request.user,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    preco_final=item['price'],
                    status='nao_lida' # Alterado de 'confirmada' para 'nao_lida'
                )
            
            return JsonResponse({'status': 'success', 'message': 'Sua reserva foi enviada para confirmação!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ocorreu um erro interno: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@login_required(login_url='/entrar/')
def minhas_reservas(request):
    # (View ajustada para continuar funcionando para o usuário final com os novos status)
    agora = timezone.now()
    reservas_usuario = Reserva.objects.filter(usuario=request.user).order_by('-data_inicio')

    # Para o usuário, "Próximas" são as que ainda não aconteceram.
    proximas = reservas_usuario.exclude(status='cancelada_pelo_usuario').filter(data_fim__gte=agora)
    
    # "Utilizadas" são as que já passaram.
    utilizadas = reservas_usuario.exclude(status='cancelada_pelo_usuario').filter(data_fim__lt=agora)
    
    # Adicionamos um novo status para cancelamento do usuário para não confundir com o sistema do admin
    canceladas = reservas_usuario.filter(status='cancelada_pelo_usuario')

    context = {
        'proximas': proximas,
        'utilizadas': utilizadas,
        'canceladas': canceladas,
    }
    return render(request, 'minhas_reservas.html', context)


@login_required(login_url='/entrar/')
@require_POST
def cancelar_reserva(request, reserva_id):
    # (Ajustado para usar um status de cancelamento específico do usuário)
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    try:
        # Usamos um status que não faz parte do fluxo do admin para não haver conflito
        reserva.status = 'cancelada_pelo_usuario'
        reserva.save()
        return JsonResponse({'status': 'success', 'message': 'Reserva cancelada com sucesso!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ----- NOVAS VIEWS PARA O PAINEL DO ADMINISTRADOR -----

@user_passes_test(is_staff_member)
def gerenciar_reservas(request):
    """ Lista todas as reservas para o administrador. """
    reservas_list = Reserva.objects.all().order_by('status', '-data_criacao')
    context = {
        'reservas': reservas_list
    }
    return render(request, 'gerenciar_reservas.html', context)


@user_passes_test(is_staff_member)
def detalhe_reserva_admin(request, reserva_id):
    """ Exibe os detalhes de uma reserva e permite ao admin alterar seu status e observações. """
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