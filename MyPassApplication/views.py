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
from .models import SessionManager
from django.http import HttpResponseRedirect
from functools import wraps



def session_login_required(view_func): # this customer decorator will check to see if the user is 
                                       # authenticated with session manager before giving them access to pages
                                       # help from: https://www.geeksforgeeks.org/creating-custom-decorator-in-django-for-different-permissions/
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        session_manager = SessionManager()
        session_manager.set_request(request)
        if not session_manager.is_authenticated():
            return HttpResponseRedirect('/login/') 
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def account(request):
    session_manager = SessionManager()
    session_manager.set_request(request)

    if session_manager.has_timed_out():
        session_manager.logout()
        messages.get_messages(request).used = True
        messages.warning(request, "Your account has been locked due to inactivity.")
        return redirect('login')

    if session_manager.is_authenticated():
        current_user = session_manager.get_current_user()
        if current_user:
            session_manager.update_last_activity()
            username = current_user.username  
            return render(request, 'account.html', {'username': username})
        else:
            return redirect('login')
    else:
        return redirect('login')



def login_view(request):
    session_manager = SessionManager()
    session_manager.set_request(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            session_manager.login(user)
            messages.get_messages(request).used = True
            messages.success(request, "You are now logged in!")
            return redirect('account')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')



@session_login_required
def vault(request):
    session_manager = SessionManager()
    session_manager.set_request(request)
    if session_manager.has_timed_out():
        session_manager.logout()
        messages.get_messages(request).used = True
        messages.warning(request, "Your account has been locked due to inactivity.")
        return redirect('login')
    
    session_manager.update_last_activity()
    return render(request, 'vault.html')



@session_login_required
def create_password(request):
    session_manager = SessionManager()
    session_manager.set_request(request)
    if session_manager.has_timed_out():
        session_manager.logout()
        messages.get_messages(request).used = True
        messages.warning(request, "Your account has been locked due to inactivity.")
        return redirect('login')
    
    session_manager.update_last_activity()
    return render(request, 'create_password.html')



def register(request):
    messages.get_messages(request).used = True
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user)  
            messages.get_messages(request).used = True
            messages.success(request, "Account created successfully!")
            return redirect('account')
        else:
            messages.get_messages(request).used = True
            messages.error(request, "There was an error in your form.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



@session_login_required
def change_password(request):
    session_manager = SessionManager()
    session_manager.set_request(request)

    if session_manager.has_timed_out():
        session_manager.logout() 
        messages.get_messages(request).used = True
        messages.warning(request, "Your account has been locked due to inactivity.")
        return redirect('login')
    
    messages.get_messages(request).used = True
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        session_manager.update_last_activity()
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.get_messages(request).used = True
            messages.success(request, 'Your password was successfully updated!')
            return redirect('account')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})



def logout_view(request):
    session_manager = SessionManager()
    session_manager.set_request(request)
    session_manager.logout()
    messages.get_messages(request).used = True
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')


