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




        
        





