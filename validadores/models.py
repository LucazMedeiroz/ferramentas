from django.db import models

# Create your models here.

#histórico de mensagens por ref e data
class Mensagem(models.Model):
    ref = models.CharField(max_length=50)
    data = models.DateTimeField(auto_now_add=True)
    mensagem = models.TextField()
    #preencher o user automaticamente
    user = models.CharField(max_length=50)
    

