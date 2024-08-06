from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required





@login_required
def logout_view(request):
    logout(request)
    
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('validadorGeral')
        else:
            return redirect('login')
    return render(request, 'home/login.html')

def home(request):
    return render(request, 'home/base.html', {'page_title':'Home'})




