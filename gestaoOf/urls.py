#urls



from django.urls import path, include

from ferramentas import settings
from gestaoOf import views
from django.conf.urls.static import static  # Import the "static" module



urlpatterns = [
    
    path('', views.producao_view, name='consulta_producao'),
    path('get-marcas/', views.get_marcas, name='get_marcas'),
    path('get-modelos/', views.get_modelos, name='get_modelos'),
    path('get-tamanhos/', views.get_tamanhos, name='get_tamanhos'),
    path('get_sorted_subofs/', views.get_sorted_subofs, name='get_sorted_subofs'),


    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


