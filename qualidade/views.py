import json
import logging
import django
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .utils import dados_qualidade
from .utils import atualizar_cancpos, atualizar_peso
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

def salvar_peso(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ref = data.get('ref')
        peso = data.get('peso')

        # Chama a função para atualizar o valor no banco de dados
        sucesso = atualizar_peso(ref, peso)

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
import socket
from .utils import obter_dados_ticket, gerar_zpl, obter_ip_impressora, obter_help_topic_id_do_ticket, obter_label_id_por_help_topic, obter_configuracao_por_id



from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse
import os

from django.http import HttpResponse


import socket
from django.http import HttpResponse
import logging

# Configure o logger
logger = logging.getLogger(__name__)

def imprimir_etiqueta_view(request, ticket_id):
    # Obter o help_topic_id do ticket
    help_topic_id = obter_help_topic_id_do_ticket(ticket_id)
    
    if not help_topic_id:
        logger.error("Help topic ID não encontrado para o ticket_id: %s", ticket_id)
        return HttpResponse("Help topic ID não encontrado", status=500)
    
    # Obter o label_id associado ao help_topic_id
    label_id = obter_label_id_por_help_topic(help_topic_id)
    if not label_id:
        logger.error("Label ID não encontrado para o help_topic_id: %s", help_topic_id)
        return HttpResponse("Label ID não encontrado", status=500)

    # Obter a configuração por ID (queries e template ZPL)
    queries, zpl_template = obter_configuracao_por_id(label_id)
    
    # Adicionando logs para verificar a consulta SQL e o template ZPL
    logger.debug(f"Consulta SQL obtida: {queries}")
    logger.debug(f"Template ZPL obtido: {zpl_template}")
    
    if not queries or not zpl_template:
        logger.error("Configuração não encontrada para o label_id: %s", label_id)
        return HttpResponse("Configuração não encontrada", status=500)

    # Obter dados do ticket usando as queries
    dados_fixos, resultados_variaveis = obter_dados_ticket(ticket_id, queries)
    
    # Adicionando logs para verificar os dados do ticket
    logger.debug(f"Dados do ticket: {dados_fixos}")
    logger.debug(f"Resultados variáveis: {resultados_variaveis}")
    
    if not dados_fixos or not resultados_variaveis:
        logger.error("Dados não encontrados para o ticket_id: %s", ticket_id)
        return HttpResponse("Dados não encontrados", status=500)
    
    # Gerar o ZPL
    zpl = gerar_zpl(ticket_id, dados_fixos, resultados_variaveis, zpl_template)
    
    # Adicionando logs para verificar o ZPL gerado
    logger.debug(f"ZPL gerado: {zpl}")
    
    if not zpl:
        logger.error("Erro ao gerar ZPL para o ticket_id: %s", ticket_id)
        return HttpResponse("Erro ao gerar ZPL", status=500)
    
    # Obter o IP da impressora
    ip_impressora = obter_ip_impressora()
    if not ip_impressora:
        logger.error("Configuração de impressora não encontrada")
        return HttpResponse("Configuração de impressora não encontrada", status=500)
    
    # Enviar o ZPL para a impressora
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip_impressora, 9100))  # Porta padrão da impressora
            sock.sendall(zpl.encode("utf-8"))
        return HttpResponse("Etiqueta impressa com sucesso")
    except Exception as e:
        logger.error("Erro ao imprimir: %s", str(e))
        return HttpResponse(f"Erro ao imprimir: {e}", status=500)


'''
def imprimir_etiqueta_view(request, ticket_id):
    # Obter o help_topic_id do ticket
    help_topic_id = obter_help_topic_id_do_ticket(ticket_id)
    
    if not help_topic_id:
        logger.error("Help topic ID não encontrado para o ticket_id: %s", ticket_id)
        return HttpResponse("Help topic ID não encontrado", status=500)
    
    # Obter o label_id associado ao help_topic_id
    label_id = obter_label_id_por_help_topic(help_topic_id)
    if not label_id:
        logger.error("Label ID não encontrado para o help_topic_id: %s", help_topic_id)
        return HttpResponse("Label ID não encontrado", status=500)

    # Obter a configuração por ID (queries e template ZPL)
    queries, zpl_template = obter_configuracao_por_id(label_id)
    
    # Adicionando logs para verificar a consulta SQL e o template ZPL
    logger.debug(f"Consulta SQL obtida: {queries}")
    logger.debug(f"Template ZPL obtido: {zpl_template}")
    
    if not queries or not zpl_template:
        logger.error("Configuração não encontrada para o label_id: %s", label_id)
        return HttpResponse("Configuração não encontrada", status=500)

    # Obter dados do ticket usando as queries
    dados_fixos, resultados_variaveis = obter_dados_ticket(ticket_id, queries)
    
    # Adicionando logs para verificar os dados do ticket
    logger.debug(f"Dados do ticket: {dados_fixos}")
    logger.debug(f"Resultados variáveis: {resultados_variaveis}")
    
    if not dados_fixos or not resultados_variaveis:
        logger.error("Dados não encontrados para o ticket_id: %s", ticket_id)
        return HttpResponse("Dados não encontrados", status=500)
    
    # Gerar o ZPL
    zpl = gerar_zpl(ticket_id, dados_fixos, resultados_variaveis, zpl_template)
    
    # Adicionando logs para verificar o ZPL gerado
    logger.debug(f"ZPL gerado: {zpl}")
    
    if not zpl:
        logger.error("Erro ao gerar ZPL para o ticket_id: %s", ticket_id)
        return HttpResponse("Erro ao gerar ZPL", status=500)
    
    # Exibir o ZPL gerado para depuração
    with open(f'zpl_output_{ticket_id}.txt', 'w', encoding='utf-8') as file:
        file.write(zpl)

    return HttpResponse("Etiqueta gerada com sucesso. Verifique o arquivo de saída para detalhes.")






def imprimir_etiqueta_view(request, ticket_id):
    # Obter o help_topic_id do ticket
    help_topic_id = obter_help_topic_id_do_ticket(ticket_id)  # Implemente ou ajuste essa função
    
    if not help_topic_id:
        return HttpResponse("Help topic ID não encontrado", status=500)
    
    # Obter dados do ticket e o template ZPL
    resultados, zpl_template = obter_dados_ticket(ticket_id, help_topic_id)
    
    if not resultados or not zpl_template:
        return HttpResponse("Configuração ou dados não encontrados", status=500)
    
    zpl = gerar_zpl(ticket_id, resultados, zpl_template)
    
    if not zpl:
        return HttpResponse("Erro ao gerar ZPL", status=500)
    
    # Obter o IP da impressora
    ip_impressora = obter_ip_impressora()
    if not ip_impressora:
        return HttpResponse("Configuração de impressora não encontrada", status=500)
    
    # Conectar-se à impressora e enviar o ZPL
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip_impressora, 9100))  # Substitua pela porta da sua impressora, se diferente
            sock.sendall(zpl.encode("utf-8"))
        return HttpResponse("Etiqueta impressa com sucesso")
    except Exception as e:
        return HttpResponse(f"Erro ao imprimir: {e}", status=500)
    


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .utils import obter_dados_ticket, gerar_zpl, obter_ip_impressora
import socket

def imprimir_etiqueta_view(request, ticket_id):
    resultados = obter_dados_ticket(ticket_id)
    zpl = gerar_zpl(ticket_id, resultados)
    
    configuracao = obter_ip_impressora()
    if not configuracao:
        return HttpResponse("Configuração não encontrada", status=500)
    
    ip_impressora = obter_ip_impressora()
    
    # Conecta à impressora e envia o ZPL
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_impressora, 9100))  # Substitua pela porta da sua impressora, se diferente
        sock.sendall(zpl.encode("utf-8"))
        sock.close()
        return HttpResponse("Etiqueta impressa com sucesso")
    except Exception as e:
        return HttpResponse(f"Erro ao imprimir: {e}", status=500)

'''