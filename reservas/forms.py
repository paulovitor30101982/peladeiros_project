from django import forms
from .models import Reserva

class ReservaAdminForm(forms.ModelForm):
    class Meta:
        model = Reserva
        # Campos que o admin poderá editar na página de detalhes
        fields = ['status', 'observacoes_admin']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control form-select'}),
            'observacoes_admin': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
        labels = {
            'status': 'Status da Reserva',
            'observacoes_admin': 'Observações (visível apenas para admins)',
        }