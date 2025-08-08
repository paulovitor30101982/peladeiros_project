from django.contrib import admin
from django import forms
# Importa todos os modelos da app 'reservas'
from .models import (
    Espaco, RegraPreco, Periodo, PrecoPeriodo, 
    Feriado, Bloqueio, BloqueioRecorrente, Reserva
)

# --- VALIDAÇÕES (copiadas do admin.py antigo) ---
class BaseFeriadoFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        feriado_count = 0
        for form in self.forms:
            if not form.is_valid() or (self.can_delete and self._should_delete_form(form)):
                continue
            if form.cleaned_data.get('aplicar_em_feriados'):
                feriado_count += 1
        if feriado_count > 1:
            raise forms.ValidationError("Erro: Apenas uma regra de preço pode ser aplicada a feriados.")

class RegraPrecoFormSet(BaseFeriadoFormSet):
    def clean(self):
        super().clean()
        horarios_por_dia = {}
        for form in self.forms:
            if not form.cleaned_data or (self.can_delete and self._should_delete_form(form)):
                continue
            dia = form.cleaned_data['dia_semana']
            inicio = form.cleaned_data['hora_inicio']
            fim = form.cleaned_data['hora_fim']
            if dia not in horarios_por_dia:
                horarios_por_dia[dia] = []
            for inicio_existente, fim_existente in horarios_por_dia[dia]:
                if max(inicio, inicio_existente) < min(fim, fim_existente):
                    raise forms.ValidationError(f"Conflito de horário para {dict(form.fields['dia_semana'].choices)[dia]}.")
            horarios_por_dia[dia].append((inicio, fim))

class PrecoPeriodoFormSet(BaseFeriadoFormSet):
    def clean(self):
        super().clean()
        periodos_por_dia = {}
        for form in self.forms:
            if not form.cleaned_data or (self.can_delete and self._should_delete_form(form)):
                continue
            dia = form.cleaned_data['dia_semana']
            periodo = form.cleaned_data['periodo']
            chave = (dia, periodo.id)
            if chave in periodos_por_dia:
                raise forms.ValidationError(f"Conflito: O período '{periodo.nome}' para {dict(form.fields['dia_semana'].choices)[dia]} já foi precificado.")
            periodos_por_dia[chave] = True

# --- INLINES ---
class RegraPrecoInline(admin.TabularInline):
    model = RegraPreco
    formset = RegraPrecoFormSet
    extra = 1
    verbose_name_plural = "Regras de Preço por Hora"

class PrecoPeriodoInline(admin.TabularInline):
    model = PrecoPeriodo
    formset = PrecoPeriodoFormSet
    extra = 1
    verbose_name_plural = "Regras de Preço por Período"

class BloqueioInline(admin.TabularInline):
    model = Bloqueio
    extra = 1
    verbose_name_plural = "Bloqueios por Data Específica"

class BloqueioRecorrenteInline(admin.TabularInline):
    model = BloqueioRecorrente
    extra = 1
    verbose_name_plural = "Bloqueios Recorrentes (Semanais)"

# --- REGISTO DOS MODELOS ---
@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'modelo_de_cobranca', 'disponivel')
    list_filter = ('tipo', 'disponivel', 'modelo_de_cobranca')
    search_fields = ('nome',)
    inlines = [
        RegraPrecoInline, 
        PrecoPeriodoInline, 
        BloqueioRecorrenteInline, 
        BloqueioInline
    ]
    class Media:
        js = ('js/admin_espaco.js',)

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'hora_inicio', 'hora_fim')

@admin.register(Feriado)
class FeriadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo_reserva', 'espaco', 'usuario', 'data_inicio', 'status', 'preco_final')
    list_filter = ('status', 'espaco')
    search_fields = ('usuario__username', 'espaco__nome', 'codigo_reserva')
    readonly_fields = ('data_criacao', 'codigo_reserva')