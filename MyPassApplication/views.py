from django.shortcuts import get_object_or_404, render, redirect
from .forms import CustomUserCreationForm, SecurityQuestionForm, UsernameForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Account, Notification, Password, SessionManager
from django.http import HttpResponseRedirect
from functools import wraps
from .handlers import Question1Handler, Question2Handler, Question3Handler
from .password_builder import PasswordDirector, SimplePasswordBuilder, ComplexPasswordBuilder, PasswordBuilder
from cryptography.fernet import Fernet
from django.conf import settings
from .mediators import UIMediator
from .components import SavedPasswords, Dashboard

# Initialize mediator
mediator = UIMediator()
# Initialize and register components
saved_passwords_component = SavedPasswords(mediator)
dashboard_component = Dashboard(mediator)

mediator.register("SavedPasswords", saved_passwords_component)
mediator.register("Dashboard", dashboard_component)



# Access the encryption key from settings
cipher_suite = Fernet(settings.ENCRYPTION_KEY)

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



# Vault view (function-based)
@session_login_required
def vault(request):
    session_manager = SessionManager()
    session_manager.set_request(request)

    if session_manager.has_timed_out():
        session_manager.logout()
        messages.warning(request, "Your account has been locked due to inactivity.")
        return redirect('login')

    session_manager.update_last_activity()
    user = session_manager.get_current_user()

    notifications = Notification.objects.filter(user=user, is_read=False)
    for notification in notifications:
        notification.is_read = True
        notification.save()

    # Retrieve all saved passwords for the current user sorted b y django built in ordering
    saved_passwords = Account.objects.filter(user=user).order_by('-id')    

    return render(request, 'vault_home.html', {'notifications': notifications, 'saved_passwords': saved_passwords})


# Mark notification as read
@session_login_required
def mark_notification_read(request, notification_id):
    session_manager = SessionManager()
    session_manager.set_request(request)
    user = session_manager.get_current_user()
    notification = get_object_or_404(Notification, id=notification_id, user=user)
    notification.is_read = True
    notification.save()
    return redirect('vault')


#builder pattern
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
    account_name = "" 
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


        # Encrypt the password before saving
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()

        # Check if the encrypted password is already in the database
        existing_password = Account.objects.filter(user=session_manager.get_current_user(), password=encrypted_password).first()
        if existing_password:
            messages.error(request, "This password already exists in your vault!")
            return render(request, 'create_password.html', {'password': password, 'account_name': account_name})

        # Save the password in the database if it's not already saved
        save_to_vault = request.POST.get('save_to_vault')
        if save_to_vault == 'yes':  # Only save if checkbox is checked
            new_account = Account.objects.create(user=session_manager.get_current_user(), name=account_name, password=encrypted_password)
            new_account.suggested = True
            new_account.save()
            messages.success(request, "Password has been saved to the Vault!")

             # Notify the mediator after password creation
        # Notify the mediator about password creation
        mediator.notify(
            sender="create_password",
            event="password_created",
            data={"id": new_account.id, "account_name": account_name, "password": password},
        )

        return render(request, 'create_password.html', {'password': password, 'account_name': account_name})

    return render(request, 'create_password.html', {'password': password})


@session_login_required
def saved_passwords(request):
    session_manager = SessionManager()
    session_manager.set_request(request)

    saved_passwords = Account.objects.filter(user=session_manager.get_current_user())
    decrypted_passwords = []

    for account in saved_passwords:
        try:
            # Decrypt the password stored in the 'password' field
            decrypted_password = cipher_suite.decrypt(account.password.encode()).decode()
            decrypted_passwords.append({
                'account': account,
                'decrypted_password': decrypted_password
            })
        except Exception as e:
            # Log the error for debugging
            print(f"Error decrypting password for account {account.name}: {e}")
            decrypted_passwords.append({
                'account': account,
                'decrypted_password': "Error decrypting password"
            })

    return render(request, 'saved_passwords.html', {'saved_passwords': decrypted_passwords})






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

@session_login_required
def delete_password(request, pk):
    session_manager = SessionManager()
    session_manager.set_request(request)

    # Ensure that only the current user can delete their passwords
    user = session_manager.get_current_user()
    password = get_object_or_404(Account, pk=pk, user=user)

    if password:
        account_name = password.name
        password.delete()

        # Notify the mediator
        mediator.notify(
            sender="delete_password",
            event="password_deleted",
            data={"account_name": account_name},
        )    
    
        messages.success(request, 'Password has been deleted successfully.')

    
    return redirect('saved_passwords')