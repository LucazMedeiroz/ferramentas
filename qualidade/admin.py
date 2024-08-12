from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Configuracao

# Define um ModelAdmin para o modelo Configuracao
class ConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ('ip_impressora', 'codigo_zpl')
    search_fields = ('ip_impressora',)

# Registra o modelo e o ModelAdmin com o admin site
admin.site.register(Configuracao, ConfiguracaoAdmin)