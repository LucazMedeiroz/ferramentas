#urls



from django.urls import path, include

from ferramentas import settings
from cartao import views
from django.conf.urls.static import static  # Import the "static" module



from django.urls import path
from . import views

urlpatterns = [
    path('', views.qualidade, name='qualidade'),
    path('qualidade/', views.qualidade, name='qualidade'),
    path('salvar_cancpos/', views.salvar_cancpos, name='salvar_cancpos'),






    





    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


