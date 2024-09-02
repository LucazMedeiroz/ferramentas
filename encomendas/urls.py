#urls



from django.urls import path, include

from ferramentas import settings
from encomendas import views
from django.conf.urls.static import static  # Import the "static" module



urlpatterns = [
    path('', views.encomendasAbertas, name='encomendas'),
    path('get_marcas', views.get_marcas, name='get_marcas'),
    path('get_modelos', views.get_modelos, name='get_modelos'),
    path('encomendas_abertas/excel/', views.encomendasAbertasExcel, name='encomendas_abertas_excel'),
    path('nave1/', views.nave1, name='nave1'),


    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


