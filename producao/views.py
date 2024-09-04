from pyexpat.errors import messages
from django.shortcuts import redirect, render
from .utils import  producao
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


from django.contrib.auth.decorators import user_passes_test

def user_in_groups(groups):
    def check_user(user):
        return user.is_authenticated and any(group.name in groups for group in user.groups.all())
    return user_passes_test(check_user)




# Create your views here.


#tabelas de produtividade


@user_in_groups(['producao', 'it'])
@login_required
def index(request):
    return render(request, 'producao/producao.html') #renderizar o template index.html


from django.shortcuts import render
from django.http import JsonResponse
from .utils import producao, get_marcas, get_modelos, get_componentes
from .utils import producao, get_seccoes, get_ct_designs

from django.shortcuts import render
from .utils import producao, get_seccoes

#login_requiered



@user_in_groups(['producao', 'it'])
@login_required
def producao_view(request):
    marca = request.GET.get('marca')
    modelo = request.GET.get('modelo')
    componente = request.GET.get('componente')
    seccao = request.GET.get('seccao')
    ct_design = request.GET.get('ct_design')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')


    start_date_default = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_date_default = datetime.now().strftime('%Y-%m-%d')



    if not seccao:
        return render(request, 'producao/producao.html', {
            'error_message': 'Por favor, selecione uma seção.',
            'seccoes': get_seccoes(),
            'start_date_default': start_date_default,
            'end_date_default': end_date_default,
            'page_title':'Produção',
        })

    filters = {
        'seccao': seccao,
        'marca': marca,
        'modelo': modelo,
        'componente': componente,
        'ct_design': ct_design,
        'start_date': start_date,
        'end_date': end_date
    }

    filters = {key: value for key, value in filters.items() if value is not None}

    rows_this_week = producao(**filters)

    from operator import itemgetter


    # Mapeamento dos dias da semana em inglês para português
    dias_da_semana = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }

    # Iterar sobre os dados e traduzir o nome do dia da semana
    producao_por_dia = {}
    for row in sorted(rows_this_week, key=itemgetter('final'), reverse=True):
        data = row['final'].strftime('%Y-%m-%d')
        # Dia da semana da data
        diasemana = row['final'].strftime('%A')
        diasemana = dias_da_semana.get(diasemana, diasemana)  # Se não houver tradução, manter o original

        if data not in producao_por_dia:
            producao_por_dia[data] = {'producao': 0, 'diasemana': diasemana}
        producao_por_dia[data]['producao'] += row['producao']



        
    context = {
        'rows_this_week': rows_this_week,
        'producao_por_dia': producao_por_dia,  # Passando o dicionário para o template
        'marca': marca,
        'modelo': modelo,
        'componente': componente,
        'seccao': seccao,
        'seccoes': get_seccoes(),
        'start_date': start_date,
        'end_date': end_date,
        'ct_design': ct_design,
        'start_date_default': start_date_default,
        'end_date_default': end_date_default,
        'page_title':'Produção',

    }

    return render(request, 'producao/producao.html', context)




def get_seccoes_view(request):
    seccoes = get_seccoes()
    return JsonResponse(seccoes, safe=False)

def get_marcas_ajax(request):
    seccao = request.GET.get('seccao')
    if seccao:
        marcas = get_marcas(seccao)
        return JsonResponse({'marcas': marcas})
    else:
        return JsonResponse({'error': 'Seção não fornecida'}, status=400)

def get_modelos_ajax(request):
    marca = request.GET.get('marca')
    if marca:
        modelos = get_modelos(marca)
        return JsonResponse({'modelos': modelos})
    else:
        return JsonResponse({'error': 'Marca não fornecida'}, status=400)

def get_componentes_ajax(request):
    modelo = request.GET.get('modelo')
    if modelo:
        componentes = get_componentes(modelo)
        return JsonResponse({'componentes': componentes})
    else:
        return JsonResponse({'error': 'Modelo não fornecido'}, status=400)
    

def get_ct_designs_ajax(request):
    seccao = request.GET.get('seccao')
    if seccao:
        ct_designs = get_ct_designs(seccao)
        return JsonResponse({'ct_designs': ct_designs})
    else:
        return JsonResponse({'error': 'Seção não fornecida'}, status=400)
    
'''
#realizar login
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        #autenticar
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'login.html') 
    return render(request, 'producao/login.html')

#realizar logout
def logout(request):
    return render(request, 'producao/logout.html')



'''

from django.shortcuts import render
from .utils import get_of_details, get_material

from django.shortcuts import render
from .utils import get_of_details, get_material

def material(request):
    results = []
    error_message = None
    falta_value = None  # Inicialize falta_value com None para garantir que sempre tenha um valor

    if request.method == 'POST':
        of = request.POST.get('of')
        if of:  # Certifique-se de que um valor foi fornecido
            of_details = get_of_details(of)
            if of_details:
                for row in of_details:
                    obrano_fo = row[0]
                    materials = get_material(obrano_fo)
                    results.append((row, materials))
                
                # Defina falta_value usando o valor da primeira linha de of_details
                falta_value = of_details[0][5]  # A coluna "FALTA" está no índice 5
            else:
                error_message = 'OF não encontrada.'
        else:
            error_message = 'Por favor, insira uma OF válida.'

    # Passe falta_value ao template mesmo que não haja resultados
    return render(request, 'producao/material.html', {'results': results, 'error_message': error_message, 'falta_value': falta_value, 'page_title':'Material'})
