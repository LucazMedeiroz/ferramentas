#urls.py producao
from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import path
#views
from .views import *
urlpatterns = [
    path('', producao_view),
    #url para a view producao_view
    path('producao/', producao_view, name='producao'), 
    path('ajax/get_marcas/', get_marcas_ajax, name='get_marcas_ajax'),
    path('ajax/get_modelos/', get_modelos_ajax, name='get_modelos_ajax'),
    path('ajax/get_componentes/', get_componentes_ajax, name='get_componentes_ajax'),
    path('ajax/get_seccoes/', get_seccoes_view, name='get_seccao'),
    path('ajax/get_ct_designs/', get_ct_designs_ajax, name='get_ct_designs_ajax'),
    path('material/', material, name='material'),







    

]

