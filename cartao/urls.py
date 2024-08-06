#urls



from django.urls import path, include

from ferramentas import settings
from cartao import views
from django.conf.urls.static import static  # Import the "static" module



from django.urls import path
from . import views

urlpatterns = [
    path('', views.cartao, name='cartao'),
    path('/download/<str:filename>/', views.download_pdf, name='download_pdf'),
    path('cartao/', views.cartao, name='cartao'), 




    





    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


