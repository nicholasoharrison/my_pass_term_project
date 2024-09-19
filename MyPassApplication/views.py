from django.shortcuts import render



def account(request):
    return render(request, 'account.html')

def login_view(request):
    return render(request, 'login.html')

def vault(request):
    return render(request, 'vault.html')

def create_password(request):
    return render(request, 'create_password.html')