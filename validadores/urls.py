#urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from validadores import views


urlpatterns = [
    path('validadorView', views.viewValidador, name='validadorView'),
    path('validadorParent', views.validadorParent, name='validadorparent'),
    path('validadorGeral', views.validadorGeral, name='validadorGeral'),
    path('fetch_versions/', views.fetch_versions, name='fetch_versions'),
    #página inicial
    path('', views.validadorGeral, name='validadorGeral'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('validadorOF', views.validarOF, name='validadorOF'),
    path('historico/', views.historico, name = 'historico'),

    

    
    




    



]

