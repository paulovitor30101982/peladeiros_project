# Arquivo: contato/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .forms import ContatoForm
from .models import MensagemContato

# --- View Pública (sem alterações) ---
def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'A sua mensagem foi enviada com sucesso! Entraremos em contacto em breve.')
            return redirect('contato:contato')
    else:
        form = ContatoForm()
    
    context = {
        'form': form
    }
    return render(request, 'contato.html', context)


# --- Views da Área Restrita (Atualizadas e Novas) ---

# Garante que apenas utilizadores com status de "staff" podem aceder
def is_staff_member(user):
    return user.is_staff

@user_passes_test(is_staff_member)
def lista_mensagens(request):
    mensagens = MensagemContato.objects.all()
    context = {
        'mensagens': mensagens
    }
    return render(request, 'lista_mensagens.html', context)

@user_passes_test(is_staff_member)
def detalhe_mensagem(request, mensagem_id):
    mensagem = get_object_or_404(MensagemContato, id=mensagem_id)
    context = {
        'mensagem': mensagem
    }
    return render(request, 'detalhe_mensagem.html', context)

@user_passes_test(is_staff_member)
def marcar_como_lida(request, mensagem_id):
    mensagem = get_object_or_404(MensagemContato, id=mensagem_id)
    if request.method == 'POST':
        mensagem.lida = True
        mensagem.save()
        messages.success(request, 'Mensagem marcada como lida.')
        return redirect('contato:detalhe_mensagem', mensagem_id=mensagem.id)
    # Se não for POST, apenas redireciona para a lista
    return redirect('contato:lista_mensagens')

@user_passes_test(is_staff_member)
def deletar_mensagem(request, mensagem_id):
    mensagem = get_object_or_404(MensagemContato, id=mensagem_id)
    if request.method == 'POST':
        mensagem.delete()
        messages.success(request, 'Mensagem apagada com sucesso.')
        return redirect('contato:lista_mensagens')
    # Se não for POST, apenas redireciona para a lista
    return redirect('contato:lista_mensagens')