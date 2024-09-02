#urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from ferramentas import settings
from home.views import logout_view, login_view, home, tempo
from validadores import views
from django.conf.urls.static import static  # Import the "static" module



urlpatterns = [

    #login

    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', logout_view, name='logout'),
    path('login/', login_view, name="login"),
    path('home/', home, name='home'),
    path('', home, name='home'),
    path('tempo/', tempo, name='tempo'),
    





] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


    

    
    




    



