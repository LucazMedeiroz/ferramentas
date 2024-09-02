import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.

import datetime


from django.shortcuts import render
import datetime
from django.shortcuts import render
from openpyxl import Workbook
from .utils import encomendasAbertasUtils, get_clientes_marcas_modelos
import datetime
from django.contrib.auth.decorators import login_required



from django.contrib.auth.decorators import user_passes_test

def user_in_groups(groups):
    def check_user(user):
        return user.is_authenticated and any(group.name in groups for group in user.groups.all())
    return user_passes_test(check_user)



@user_in_groups(['encomendas', 'it'])
@login_required
def encomendasAbertas(request):

    
    data = get_clientes_marcas_modelos()




    clientes = {item['cliente'] for item in data}
    #ordernar clientes
    clientes = sorted(clientes)

    marcas = {item['marca'] for item in data}
    modelos = {item['modelo'] for item in data}

            #data de hoje ou de ontem
    hoje = datetime.datetime.today()
    ontem = hoje - datetime.timedelta(days=1)
    amanha = hoje + datetime.timedelta(days=1)
    doisdias = hoje + datetime.timedelta(days=2)

    hoje_str = hoje.strftime("%Y-%m-%d")
    ontem_str = ontem.strftime("%Y-%m-%d")
    amanha_str = amanha.strftime("%Y-%m-%d")
    doisdias_str = doisdias.strftime("%Y-%m-%d")

    #semana atual
    semana_atual = hoje.strftime("%Y-W%U")
    




    if request.method == 'POST':
        inicio_semana = request.POST.get('inicio')
        fim_semana = request.POST.get('fim')
        cliente = request.POST.get('cliente')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')

        #obter o primeiro dia da semana (inicio_semana) e o ultimo dia de (fim_semana)
        def get_start_date_of_week(week_str):
            year, week = map(int, week_str.split('-W'))
            first_day_of_week = datetime.datetime.strptime(f'{year}-W{week-1}-1', "%Y-W%U-%w").date()
            return first_day_of_week

        def get_end_date_of_week(week_str):
            start_date = get_start_date_of_week(week_str)
            end_date = start_date + datetime.timedelta(days=6)
            return end_date

        inicio = get_start_date_of_week(inicio_semana)
        fim = get_end_date_of_week(fim_semana)
        dados = encomendasAbertasUtils(inicio, fim, cliente, marca, modelo)
        #add uma nova coluna na lista de dados


        #adicionar uma coluna na lista de dados com o nome cor:

        """
                                                        {% elif amanha == detalhe.data_para_entrega|date:"Y-m-d" and detalhe.em_aberto > detalhe.estoque_armazem %}
                                                    <td style="background-color: #ff000038">{{ detalhe.data_para_entrega|date:"Y-m-d" }}</td>
                                                {% elif hoje >= detalhe.data_para_entrega|date:"Y-m-d" and detalhe.em_aberto > detalhe.estoque_armazem %}
                                                    <td style="background-color: #ff000038">{{ detalhe.data_para_entrega|date:"Y-m-d" }}</td>
                                                {% elif hoje > detalhe.data_para_entrega|date:"Y-m-d" and detalhe.em_aberto > detalhe.estoque_armazem %}
                                                    <td style="background-color: #ff000038">{{ detalhe.data_para_entrega|date:"Y-m-d" }}</td>
                                                {% elif doisdias == detalhe.data_para_entrega|date:"Y-m-d" and detalhe.em_aberto > detalhe.estoque_armazem %}
                                                    <td style="background-color: #ffa60083">{{ detalhe.data_para_entrega|date:"Y-m-d" }}</td>
                                                {% else %}
                                                    <td>{{ detalhe.data_para_entrega|date:"Y-m-d" }} - {{ detalhe.data_para_entrega_menos_um|date:"Y-m-d" }}</td>
                                                {% endif %}
                """

        for item in dados:
            cores = []  # Lista para armazenar as cores dos detalhes do item
            for detalhe in item['detalhes']:
                data_entrega_str = detalhe['data_para_entrega'].strftime("%Y-%m-%d")
                
                if detalhe['estoque_armazem'] >= detalhe['em_aberto']:
                    cores.append('green')
                elif amanha_str == data_entrega_str and detalhe['em_aberto'] > detalhe['estoque_armazem']:
                    cores.append('red')
                elif hoje_str >= data_entrega_str and detalhe['em_aberto'] > detalhe['estoque_armazem']:
                    cores.append('red')
                elif hoje_str > data_entrega_str and detalhe['em_aberto'] > detalhe['estoque_armazem']:
                    cores.append('red')
                elif doisdias_str == data_entrega_str and detalhe['em_aberto'] > detalhe['estoque_armazem']:
                    cores.append('orange')
                else:
                    cores.append('black')


            # Determina a cor do item baseado nas cores dos detalhes
            cores1 = 0
            verde = 0
            vermelho = 0
            laranja = 0
            black = 0
            for cor in cores:


                if cor == 'red':
                    vermelho += 1
                elif cor == 'green':
                    verde += 1
                elif cor == 'orange':
                    laranja += 1
                elif cor == 'black':
                    black += 1
                
                cores1 += 1
                
                if vermelho > 0:
                    item['cor'] = 'red'
                elif laranja > 0 and vermelho == 0:
                    item['cor'] = 'orange'
                elif verde == cores1 and laranja == 0 and vermelho == 0 and black == 0:
                    item['cor'] = 'green'
                else:
                    item['cor'] = 'black'
                
                
    




        #print de cores
        print('-----------------Cores---------------------------')
        for item in dados:
            print(item['cor'])
            
    
            
                    
  

            

                




            
            









 








        return render(request, 'encomendas/encomendas.html', {'dados': dados, 'inicio':inicio_semana, 'fim':fim_semana, 'clientes': clientes, 'marcas': marcas, 'modelo': modelo, 'cliente':cliente, 'marca':marca, 'modelo':modelo, 'hoje': hoje_str, 'ontem':ontem_str, 'doisdias':doisdias_str, 'amanha':amanha_str, 'page_title':'Encomendas', 'semana_atual': semana_atual})
    
    return render(request, 'encomendas/encomendas.html', {'clientes': clientes, 'marcas': marcas, 'modelos': modelos, 'amanha':amanha_str, 'hoje':hoje_str, 'page_title':'Encomendas',  'semana_atual': semana_atual})
    


from django.http import JsonResponse

from .utils import get_clientes_marcas_modelos

def get_marcas(request):
    cliente_id = request.GET.get('cliente_id')

    # Obter todos os dados de clientes, marcas e modelos
    data = get_clientes_marcas_modelos()

    # Criar um conjunto de marcas
    marcas = set()

    # Se um cliente específico for selecionado
    if cliente_id:
        for item in data:
            if item['cliente'] == cliente_id:
                marcas.add(item['marca'])
    else:
        # Se nenhum cliente específico for selecionado, mostrar todas as marcas
        for item in data:
            marcas.add(item['marca'])

    # Retornar marcas como JSON
    return JsonResponse({'marcas': sorted(list(marcas))})


def get_modelos(request):
    marca_id = request.GET.get('marca_id')
    data = get_clientes_marcas_modelos()
    
    modelos = {item['modelo'] for item in data if item['marca'] == marca_id}
    return JsonResponse({'modelos': sorted(modelos)})







# View para gerar o Excel
def encomendasAbertasExcel(request):
    if request.method == 'POST':
        inicio_semana = request.POST.get('inicio')
        fim_semana = request.POST.get('fim')
        cliente = request.POST.get('cliente')
        marca = request.POST.get('marca')
        modelo = request.POST.get('modelo')

        def get_start_date_of_week(week_str):
            year, week = map(int, week_str.split('-W'))
            first_day_of_week = datetime.datetime.strptime(f'{year}-W{week-1}-1', "%Y-W%U-%w").date()
            return first_day_of_week

        def get_end_date_of_week(week_str):
            start_date = get_start_date_of_week(week_str)
            end_date = start_date + datetime.timedelta(days=6)
            return end_date

        inicio = get_start_date_of_week(inicio_semana)
        fim = get_end_date_of_week(fim_semana)
        dados = encomendasAbertasUtils(inicio, fim, cliente, marca, modelo)

        # Create an Excel workbook and sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Encomendas Abertas"

        # Headers for the Excel sheet
        headers = ["Obra No", "Ref", "Design", "Marca", "Modelo", "Quantidade", "Entregue", "Em Aberto", "Data Para Entrega", "Tamanho", "Estoque Armazém"]
        ws.append(headers)

        # Adding data to the sheet
        for item in dados:
            for detalhe in item['detalhes']:
                ws.append([
                    detalhe['obrano'],
                    detalhe['ref'],
                    detalhe['design'],
                    detalhe['MARCA'],
                    detalhe['MODELO'],
                    detalhe['qtt'],
                    detalhe['entregue'],
                    detalhe['em_aberto'],
                    detalhe['data_para_entrega'],
                    detalhe['tamanho'],
                    detalhe['estoque_armazem']
                ])

        # Prepare the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=encomendas_abertas.xlsx'
        wb.save(response)

        return response

    return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.shortcuts import render
from .utils import fetch_id_versions, fetch_nave1_data, fetch_marca_modelo_tamanho,fetch_nave1_data_nao_produzido


# Atualização na função de organização de dados no views.py

def nave1(request):
    id_versions = fetch_id_versions()
    organized_data = {}

    for id_version in id_versions:
        produced_rows = fetch_nave1_data(id_version)
        
        for row in produced_rows:
            ref = row[8]
            lang4 = row[0]
            stock_produzido = row[2]
            marca, modelo, tamanho = fetch_marca_modelo_tamanho(ref)
            obrano_of = row[3]
            ofparent = row[4]
            status = row[5]
            qtt_real = row[6]
            qtt_produzida = row[7]
            status_sub = row[9]
            sequencial = row[10]

            key = (marca, modelo, tamanho)
            
            if key not in organized_data:
                organized_data[key] = {
                    'subdata': [],
                    'lang4': {},
                    'nao_produzido': {}
                }
            
            organized_data[key]['subdata'].append({
                'ref': ref,
                'obrano_of': obrano_of,
                'ofparent': ofparent,
                'status': status,
                'qtt_real': qtt_real,
                'qtt_produzida': qtt_produzida,
                'status_sub': status_sub,
                'sequencial': sequencial
            })
            
            organized_data[key]['lang4'][lang4] = stock_produzido
        
        nao_produzido_rows = fetch_nave1_data_nao_produzido(id_version)
        for row in nao_produzido_rows:
            lang4 = row[0]
            stock_nao_produzido = row[1]
            marca = row[2]
            modelo = row[3]
            tamanho = row[4]

            key = (marca, modelo, tamanho)
            
            if key not in organized_data:
                organized_data[key] = {
                    'subdata': [],
                    'lang4': {},
                    'nao_produzido': {}
                }

            organized_data[key]['nao_produzido'][lang4] = stock_nao_produzido
    
    lang4_keys = ['CS', 'SS', 'DRP', 'MB', 'HT', 'DT', 'TT', 'ST']
    
    return render(request, 'encomendas/nave1.html', {
        'data': organized_data,
        'lang4_keys': lang4_keys,
    })
