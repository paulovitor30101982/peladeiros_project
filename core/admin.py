from django.contrib import admin
from django import forms
# Importando o novo modelo BloqueioRecorrente
from .models import Usuario, Espaco, RegraPreco, Periodo, PrecoPeriodo, Feriado, Bloqueio, BloqueioRecorrente

# --- VALIDAÇÃO DE SEGURANÇA PARA REGRAS DE FERIADO ADICIONADA ---
class BaseFeriadoFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        feriado_count = 0
        for form in self.forms:
            # Ignora formulários que serão deletados ou que não têm dados
            if self.can_delete and self._should_delete_form(form):
                continue
            if form.cleaned_data and form.cleaned_data.get('aplicar_em_feriados'):
                feriado_count += 1
        
        if feriado_count > 1:
            raise forms.ValidationError(
                "Erro de Validação: Você só pode ter uma regra de preço designada como padrão para feriados por cada modelo de cobrança (Hora ou Período). "
                "Por favor, desmarque as regras extras antes de salvar."
            )

# --- VALIDAÇÃO CONTRA CONFLITOS PARA PREÇO POR HORA (CORRIGIDA) ---
class RegraPrecoFormSet(BaseFeriadoFormSet): # Herda da validação de feriado
    def clean(self):
        super().clean()
        horarios_por_dia = {}
        for form in self.forms:
            # CORREÇÃO: Pula o form se ele estiver vazio ou marcado para deleção
            if not form.cleaned_data or (self.can_delete and self._should_delete_form(form)):
                continue

            dia = form.cleaned_data['dia_semana']
            inicio = form.cleaned_data['hora_inicio']
            fim = form.cleaned_data['hora_fim']

            if dia not in horarios_por_dia:
                horarios_por_dia[dia] = []

            for inicio_existente, fim_existente in horarios_por_dia[dia]:
                if max(inicio, inicio_existente) < min(fim, fim_existente):
                    raise forms.ValidationError(
                        f"Conflito de horário detectado para {dict(form.fields['dia_semana'].choices)[dia]}: "
                        f"o período de {inicio.strftime('%H:%M')} a {fim.strftime('%H:%M')} "
                        f"conflita com o período já definido de {inicio_existente.strftime('%H:%M')} a {fim_existente.strftime('%H:%M')}."
                    )
            horarios_por_dia[dia].append((inicio, fim))

# --- VALIDAÇÃO CONTRA CONFLITOS PARA PREÇO POR PERÍODO (CORRIGIDA) ---
class PrecoPeriodoFormSet(BaseFeriadoFormSet): # Herda da validação de feriado
    def clean(self):
        super().clean()
        periodos_por_dia = {}
        for form in self.forms:
            # CORREÇÃO: Pula o form se ele estiver vazio ou marcado para deleção
            if not form.cleaned_data or (self.can_delete and self._should_delete_form(form)):
                continue

            dia = form.cleaned_data['dia_semana']
            periodo = form.cleaned_data['periodo']
            
            chave = (dia, periodo.id)
            if chave in periodos_por_dia:
                raise forms.ValidationError(
                    f"Conflito detectado: O período '{periodo.nome}' para "
                    f"{dict(form.fields['dia_semana'].choices)[dia]} já foi precificado. "
                    f"Você não pode ter dois preços para o mesmo período no mesmo dia/grupo de dias."
                )
            periodos_por_dia[chave] = True


# --- INLINES USANDO OS FORMSETS DE VALIDAÇÃO ---
class RegraPrecoInline(admin.TabularInline):
    model = RegraPreco
    formset = RegraPrecoFormSet
    extra = 1
    verbose_name = "Regra de Preço por Hora"
    # Título simplificado para o JavaScript encontrar
    verbose_name_plural = "Regras de Preço por Hora"

class PrecoPeriodoInline(admin.TabularInline):
    model = PrecoPeriodo
    formset = PrecoPeriodoFormSet
    extra = 1
    verbose_name = "Regra de Preço por Período"
    # Título simplificado para o JavaScript encontrar
    verbose_name_plural = "Regras de Preço por Período"

class BloqueioInline(admin.TabularInline):
    model = Bloqueio
    extra = 1
    verbose_name_plural = "Bloqueios por Data Específica"

# --- NOVO INLINE PARA BLOQUEIOS RECORRENTES ---
class BloqueioRecorrenteInline(admin.TabularInline):
    model = BloqueioRecorrente
    extra = 1
    verbose_name_plural = "Bloqueios Recorrentes (Semanais)"

@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'modelo_de_cobranca', 'capacidade', 'disponivel')
    list_filter = ('tipo', 'disponivel', 'modelo_de_cobranca')
    search_fields = ('nome', 'descricao')
    # Adicionado o novo inline de bloqueio recorrente
    inlines = [RegraPrecoInline, PrecoPeriodoInline, BloqueioRecorrenteInline, BloqueioInline]

    # Classe para incluir nosso JavaScript customizado na página do admin
    class Media:
        js = ('js/admin_espaco.js',)

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'hora_inicio', 'hora_fim')

@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data')
    list_filter = ('data',)