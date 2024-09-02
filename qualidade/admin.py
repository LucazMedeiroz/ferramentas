from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import HelpTopicLabelMapping

# Define um ModelAdmin para o modelo Configuracao

# admin.py


@admin.register(HelpTopicLabelMapping)
class HelpTopicLabelMappingAdmin(admin.ModelAdmin):
    list_display = ('help_topic_id', 'label_id')
    search_fields = ('help_topic_id', 'label_id')
