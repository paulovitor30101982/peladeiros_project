from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

# Certifique-se de que está a importar o formulário correto
from .forms import ContatoForm
from .models import MensagemContato

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'A sua mensagem foi enviada com sucesso! Entraremos em contacto em breve.')
            return redirect('contato:contato')
    else:
        # Esta linha cria uma instância vazia do formulário quando a página é carregada
        form = ContatoForm()
    
    # Esta linha envia o formulário para o template dentro de um dicionário chamado 'context'
    context = {
        'form': form
    }
    return render(request, 'contato.html', context)


@user_passes_test(lambda u: u.is_staff)
def lista_mensagens(request):
    mensagens = MensagemContato.objects.all()
    context = {
        'mensagens': mensagens
    }
    return render(request, 'lista_mensagens.html', context)