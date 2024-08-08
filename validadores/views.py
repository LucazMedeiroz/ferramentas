from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .models import Mensagem
from .utils import queryValidador, queryValidadorSRef, queryValidadorOF, updateOf
from django.contrib.auth import logout
from django.contrib.auth import login




# Create your views here.


# Path: validadores/views.py


from django.contrib.auth.decorators import user_passes_test

def user_in_groups(groups):
    def check_user(user):
        return user.is_authenticated and any(group.name in groups for group in user.groups.all())
    return user_passes_test(check_user)



#verificar se o campo imp e da_entreada são iguais


@user_in_groups(['validadores', 'it'])
@login_required
def viewValidador(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')
        version = request.POST.get('version')



        dados = queryValidador(ref)
        print(dados)

  
        erros = []
        count = 0



        versoes = []
        for row in dados:
            if row[1] not in versoes:
                versoes.append(row[1])

        if version != row[1]:
            for row in dados:
                if row[18] == 0 and row[19] not in (0, None):
                    count += 1
                    erros.append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 0 ou null, ref {ref} da versão {row[1]}")
                elif row[18] == 1 and row[19] != 1:
                    count += 1
                    erros.append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 1, ref {ref} da versão {row[1]}")
        else:
            for row in dados:
                if row[1] == version:
                    if row[18] == 0 and row[19] not in (0, None):
                        count += 1
                        erros.append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 0 ou null, ref {ref} da versão {row[1]}")
                    elif row[18] == 1 and row[19] != 1:
                        count += 1
                        erros.append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 1, ref {ref} da versão {row[1]}")
        
        print(dados)
        print(erros)
        #capturar o user logado
        
        utilizador = request.user
        print(utilizador)


        #gravar erros no histórico
        if count > 0:
            for erro in erros:
                Mensagem.objects.create(ref=ref, mensagem=erro, user=utilizador)

        if erros:
            return render(request, 'validadores/validador.html', {'dados': dados, 'erros': erros, 'total': count, 'ref': ref, 'version':version, 'versoes':versoes, 'page_title':'Validador da Gama'})
        else:
            return render(request, 'validadores/validador.html', {'dados': dados, 'ref': ref, 'version':version, 'versoes':versoes, 'page_title':'Validador de Gama'})
    else:
        dados = []
        return render(request, 'validadores/validador.html', {'dados': dados, 'page_title':'Valiudador de Gama'})
    
    
    
    
    

        

@user_in_groups(['validadores', 'it'])
@login_required
def validadorParent(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')
        version = request.POST.get('version')
        dados = queryValidador(ref)

        print(f"Ref: {ref}, Version: {version}")
        print(f"Dados: {dados}")

        erros = []
        count = 0
        ids = []
        versoes = []

        # Track versions
        for row in dados:
            if row[1] not in versoes:
                versoes.append(row[1])

        print(f"Versões: {versoes}")

        # Collect ids based on version
        for row in dados:
            if not version or row[1] == version:
                if row[21]:
                    ids.append(row[21])

        print(f"IDs: {ids}")

        # Error checks for validadorParent logic
        for row in dados:
            if  version != row[1] or row[1] == version:
                if row[22] > 0 and row[22] not in ids:
                    count += 1
                    erros.append(f"Erro no parent {row[22]}, ref {ref} da versão {row[1]}")

        print(f"Erros: {erros}")
        print(f"Total de erros: {count}")

        utilizador = request.user



        if count > 0:
            for erro in erros:
                Mensagem.objects.create(ref=ref, mensagem=erro, user=utilizador)

        context = {
            'dados': dados,
            'erros': erros,
            'total': count,
            'ref': ref,
            'version': version,
            'versoes': versoes
        }

        return render(request, 'validadores/validadorParent.html', context)
    else:
        return render(request, 'validadores/validadorParent.html', {'dados': [], 'page_title':'Validador de Gama'})





    
from django.views.decorators.csrf import csrf_exempt

@user_in_groups(['validadores', 'it'])
@login_required
@csrf_exempt
def fetch_versions(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')
        dados = queryValidador(ref)

        versoes = []
        for row in dados:
            if row[1] not in versoes:
                versoes.append(row[1])

        print(versoes)

        return JsonResponse({'versions': versoes})
    

#validador que execulta a logica da view de validadorView e validadorParent:




@user_in_groups(['validadores', 'it'])
@login_required
def validadorGeral(request):
    if request.method == 'POST':
        refs = request.POST.get('refs')
        ref_list = refs.split(',') if refs else [request.POST.get('ref')]
        version = request.POST.get('version')

        all_dados = []
        all_erros = {}
        count = 0
        versoes = []

        for ref in ref_list:
            ref = ref.strip()
            dados = queryValidador(ref)
            all_dados.extend(dados)
            all_erros[ref] = {'parent_errors': [], 'da_entrada_errors': []}

            # Track versions
            for row in dados:
                if row[1] not in versoes:
                    versoes.append(row[1])

            # Error checks for viewValidador logic
            for row in dados:
                if not version or row[1] == version:
                    if row[18] == 0 and row[19] not in (0, None):
                        all_erros[ref]['da_entrada_errors'].append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 0 ou null, ref {ref} da versão {row[1]}")
                    elif row[18] == 1 and row[19] != 1:
                        all_erros[ref]['da_entrada_errors'].append(f"Erro na op {row[20]}: campo 'da_entrada' deve ser 1, ref {ref} da versão {row[1]}")

            # Error checks for validadorParent logic
            ids = [row[21] for row in dados if row[21]]
            for row in dados:
                if not version or row[1] == version:
                    if row[22] > 0 and row[22] not in ids:
                        all_erros[ref]['parent_errors'].append(f"Erro no parent {row[22]}, ref {ref} da versão {row[1]}")

        count = sum(len(errors['parent_errors']) + len(errors['da_entrada_errors']) for errors in all_erros.values())

        #identificar o user
        utilizador = request.user
        print(utilizador)




        if count > 0:
            for erro in all_erros:
                print(utilizador)
                Mensagem.objects.create(ref=ref, mensagem=erro, user='roberto')

        context = {
            'dados': all_dados,
            'erros': all_erros,
            'total': count,
            'refs': refs,
            'version': version,
            'versoes': versoes,
            'user': utilizador,
            'page_title':'Validador de Gama'

        }

        return render(request, 'validadores/validadorGeral.html', context)
    else:
        return render(request, 'validadores/validadorGeral.html', {'dados': [], 'page_title':'Validador de Gama'})
    


@user_in_groups(['validadores', 'it'])
@login_required
def validarOF(request):
    if request.method == 'POST':
        of = request.POST.get('of')
        dados = queryValidadorOF(of)
        fechadas = True
        


        erros = []
        erro = ''


        print(dados)

        for row in dados:
            if row[9] == None or row[10] == None:
                fechadas = False
                erros.append(f"campos 'initial' e 'final' devem ser preenchidos")

        
        for row in dados:
            if row[0] == 1 or row[1] == 1:
                if fechadas == True:
                    erro = 'campos "play" e "stop" devem ser 0' 
                    if erro not in erros:
                        erros.append(erro)
                        updateOf(of)
 

        print(erros)
        utilizador = request.user
        if erros:
            for erro in erros:
                Mensagem.objects.create(ref=of, mensagem=erro, user = utilizador)

        if erros:
            return render(request, 'validadores/validadorOF.html', {'dados': dados, 'erros': erros, 'of': of, 'page_title':'Validador OF '})
        else:
            return render(request, 'validadores/validadorOF.html', {'dados': dados, 'of': of, 'page_title':'Validador OF '})
    else:
        dados = []
        return render(request, 'validadores/validadorOF.html', {'dados': dados, 'page_title':'Validador OF'})
    

from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Mensagem

@user_in_groups(['validadores', 'it'])
def historico(request):
    mensagens_list = Mensagem.objects.all().order_by('-id')
    paginator = Paginator(mensagens_list, 10)  # 10 mensagens por página

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'validadores/historico.html', {'page_obj': page_obj, 'page_title':'Histórico'})


    






















