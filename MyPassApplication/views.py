from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required


@login_required
def account(request):
    return render(request, 'account.html')

def login_view(request):
    return render(request, 'login.html')

def vault(request):
    return render(request, 'vault.html')

def create_password(request):
    return render(request, 'create_password.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})