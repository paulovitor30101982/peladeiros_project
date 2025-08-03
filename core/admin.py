# Arquivo: core/admin.py

from django.contrib import admin
# Importe os novos modelos que você criou
from .models import Usuario, Espaco, RegraPreco, Bloqueio

# Registre os modelos aqui para que eles apareçam no painel de admin

# Customização para exibir as regras de preço e bloqueios junto com o Espaço
class RegraPrecoInline(admin.TabularInline):
    model = RegraPreco
    extra = 1 # Quantos formulários em branco de regras de preço mostrar

class BloqueioInline(admin.TabularInline):
    model = Bloqueio
    extra = 1 # Quantos formulários em branco de bloqueios mostrar

@admin.register(Espaco)
class EspacoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'capacidade', 'disponivel')
    list_filter = ('tipo', 'disponivel')
    search_fields = ('nome', 'descricao')
    inlines = [RegraPrecoInline, BloqueioInline]

# Registro simples para os outros modelos (se precisar editá-los separadamente)
admin.site.register(RegraPreco)
admin.site.register(Bloqueio)

# Você pode manter o registro do seu usuário customizado aqui se desejar
# Exemplo: admin.site.register(Usuario)