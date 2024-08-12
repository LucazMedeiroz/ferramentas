from django.db import models

# Create your models here.
class Configuracao(models.Model):
    ip_impressora = models.CharField(max_length=15, default='192.168.122.64')
    codigo_zpl = models.TextField(default="""
    ^XA
    ^CF0,20
    ^FO40,20^BQN,2,3^FR^FDMA,{{ticket_number}}^FS
    {{etiquetas}}
    ^XZ
    """)

    


    