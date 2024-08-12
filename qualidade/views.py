import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .utils import dados_qualidade
from .utils import atualizar_cancpos
from django.http import JsonResponse



# Create your views here.



# View para gerar o Excel



from django.contrib.auth.decorators import user_passes_test

def user_in_groups(groups):
    def check_user(user):
        return user.is_authenticated and any(group.name in groups for group in user.groups.all())
    return user_passes_test(check_user)



#@user_in_groups(['qualidade', 'it', 'qualidade_admin'])
def qualidade(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')
        dados = dados_qualidade(ref)
        print('-----------dados view ''''''''''''')
        print(dados)

        #verificar a que grupo pertence
        is_qualidade_admin = request.user.groups.filter(name='qualidade_admin').exists()

        context = {
            'dados': dados,
            'ref': ref,
            'is_qualidade_admin': is_qualidade_admin,
            'page_title': 'Qualidade',



        }

        return render(request, 'qualidade/qualidade.html', context)
    

    context = {
        'page_title': 'Qualidade',
        }


    return render(request, 'qualidade/qualidade.html', context)

def salvar_cancpos(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ref = data.get('ref')
        cancpos = data.get('cancpos')

        # Chama a função para atualizar o valor no banco de dados
        sucesso = atualizar_cancpos(ref, cancpos)

        if sucesso:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})




from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from zebra import Zebra
import qrcode
from io import BytesIO
import socket
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from zebra import Zebra
import qrcode
from io import BytesIO
import socket
from .models import  Configuracao  # Importar o modelo de Ticket e Configuração



from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Configuracao
from .utils import obter_dados_ticket, gerar_zpl
import socket

def imprimir_etiqueta_view(request, ticket_id):
    resultados = obter_dados_ticket(ticket_id)
    zpl = gerar_zpl(ticket_id, resultados)
    
    configuracao = Configuracao.objects.first()
    if not configuracao:
        return HttpResponse("Configuração não encontrada", status=500)
    
    ip_impressora = configuracao.ip_impressora
    
    # Conecta à impressora e envia o ZPL
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_impressora, 9100))  # Substitua pela porta da sua impressora, se diferente
        sock.sendall(zpl.encode("utf-8"))
        sock.close()
        return HttpResponse("Etiqueta impressa com sucesso")
    except Exception as e:
        return HttpResponse(f"Erro ao imprimir: {e}", status=500)
