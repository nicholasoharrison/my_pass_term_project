import email
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def account(request):
    return render(request, 'account.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('account')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')

@login_required
def vault(request):
    return render(request, 'vault.html')

@login_required
def create_password(request):
    return render(request, 'create_password.html')

def register(request):
    messages.get_messages(request).used = True
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user)  
            messages.success(request, "Account created successfully!")
            return redirect('account')
        else:
            messages.error(request, "There was an error in your form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def change_password(request):
    messages.get_messages(request).used = True
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})