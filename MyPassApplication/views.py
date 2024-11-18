import email
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CustomUserCreationForm, SecurityQuestionForm, UsernameForm, EditPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import SessionManager, Password, Account
from django.http import HttpResponseRedirect
from functools import wraps
from .handlers import Question1Handler, Question2Handler, Question3Handler
from .password_builder import PasswordDirector, SimplePasswordBuilder, ComplexPasswordBuilder, PasswordBuilder


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


#Test
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

    current_user = session_manager.get_current_user()

    user_accounts = Account.objects.filter(user = current_user)
    return render(request, 'vault.html', {'user_accounts': user_accounts})



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


    password = None
    if request.method == 'POST':
        account_name = request.POST.get('account_name')
        complexity = request.POST.get('complexity')
        custom_password = request.POST.get('custom_password')
        
        if custom_password:
            password = custom_password
            messages.success(request, "Your custom password has been saved.")
        else:
            if complexity == 'simple':
                builder = SimplePasswordBuilder()
            elif complexity == 'complex':
                builder = ComplexPasswordBuilder()
            else:
                messages.error(request, 'Invalid password complexity selection.')
                return render(request, 'create_password.html')

            director = PasswordDirector(builder)
            password = director.create_password()
            
        current_user = session_manager.get_current_user()

        messages.success(request, f"Generated Password: {password}")
        Account.objects.create(user=current_user, name=account_name, password=password)
        return redirect('vault')

    return render(request, 'create_password.html', {'password': password})



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
        else:
            messages.error(request, 'There was an error with your registration.')
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



def enter_username(request):
    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                request.session['username'] = username
                request.session['current_question'] = 'favorite_color'
                return redirect('forgot_password')
            except User.DoesNotExist:
                messages.error(request, "Username not found.")
        return render(request, 'enter_username.html', {'form': form})
    else:
        form = UsernameForm()
    return render(request, 'enter_username.html', {'form': form})



def forgot_password(request):
    if 'username' not in request.session:
        return redirect('enter_username')

    username = request.session['username']
    user = User.objects.get(username=username)
    print(f"Username stored in session: {request.session.get('username')}")
    
    first_handler = Question1Handler()
    second_handler = Question2Handler()
    third_handler = Question3Handler()

    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        
        if form.is_valid():
            answer = form.cleaned_data['answer']
            
            current_question = request.session.get('current_question', 'favorite_color')

            if current_question == 'favorite_color':
                if first_handler.handle(user, answer):
                    request.session['current_question'] = 'birth_city'
                    form = SecurityQuestionForm()
                    messages.success(request, "Correct! Next question.")
                else:
                    messages.error(request, "Incorrect answer.")
                    return render(request, 'forgot_password.html', {'form': form})

            elif current_question == 'birth_city':
                if second_handler.handle(user, answer):
                    request.session['current_question'] = 'first_employer'
                    form = SecurityQuestionForm()
                    messages.success(request, "Correct! Next question.")
                else:
                    messages.error(request, "Incorrect answer.")
                    return render(request, 'forgot_password.html', {'form': form})

            elif current_question == 'first_employer':
                if third_handler.handle(user, answer):
                    messages.success(request, "All answers correct! You can now reset your password.")
                    return redirect('password_reset')
                else:
                    messages.error(request, "Incorrect answer.")
                    return render(request, 'forgot_password.html', {'form': form})
    else:
        form = SecurityQuestionForm()

    return render(request, 'forgot_password.html', {'form': form})



def password_reset(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist. Please check your username.')

    return render(request, 'password_reset.html')



def edit_password(request, password_id):
    session_manager = SessionManager()
    current_user = session_manager.get_current_user()
    account = get_object_or_404(Account, id=password_id, user=current_user)

    if request.method == 'POST':
        form = EditPasswordForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('vault')
    else:
        form = EditPasswordForm(instance=account)

    return render(request, 'edit_password.html', {'form': form, 'account': account})

def delete_password(request, password_id):
    session_manager = SessionManager()
    current_user = session_manager.get_current_user()
    account = get_object_or_404(Account, id=password_id, user=current_user)

    if request.method == 'POST':
        account.delete()
        return redirect('vault') 

    return render(request, 'confirm_delete.html', {'account': account})