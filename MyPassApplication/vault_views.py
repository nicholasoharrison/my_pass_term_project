from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import View, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.http import Http404
from .models import Login, CreditCard, Identity, SecureNote, SessionManager
from .forms import LoginForm, CreditCardForm, IdentityForm, SecureNoteForm
from .views import session_login_required 
from .views import mediator
from django.apps import apps
import pyperclip
from datetime import date, timedelta



class BaseVaultView(View):
    session_manager = None

    def dispatch(self, request, *args, **kwargs):
        self.session_manager = SessionManager()
        self.session_manager.set_request(request)
        if not self.session_manager.is_authenticated():
            return redirect('login')
        if self.session_manager.has_timed_out():
            self.session_manager.logout()
            messages.warning(request, "Your account has been locked due to inactivity.")
            return redirect('login')
        self.session_manager.update_last_activity()
        return super().dispatch(request, *args, **kwargs)


# Mixin ensures that users can only access objects that belong to them.
class UserObjectMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.user != self.session_manager.get_current_user():
            raise Http404("You do not have permission to access this item.")
        return obj
class UserFormValidMixin:
    def form_valid(self, form):
        form.instance.user = self.session_manager.get_current_user()
        return super().form_valid(form)    
    
# Vault Home View
@method_decorator(session_login_required, name='dispatch')
class VaultHomeView(BaseVaultView, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'vault_home.html')

# Views for Login Data Type
@method_decorator(session_login_required, name='dispatch')
class LoginListView(BaseVaultView, ListView):
    model = Login
    template_name = 'login_list.html'
    context_object_name = 'logins'

    def get_queryset(self):
        user = self.session_manager.get_current_user()
        return Login.objects.filter(user=user)

@method_decorator(session_login_required, name='dispatch')
class LoginCreateView(BaseVaultView, UserFormValidMixin, CreateView):
    model = Login
    form_class = LoginForm
    template_name = 'login_form.html'
    success_url = reverse_lazy('login_list')

    def form_valid(self, form):
        messages.success(self.request, 'Login item added successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class LoginDetailView(BaseVaultView, UserObjectMixin, DetailView):
    model = Login
    template_name = 'login_detail.html'
    context_object_name = 'login'

    # """"""
    # code Michael Sepsey
    # """"""
    def copy_URL(self):
        pyperclip.copy(self.object.site_url)
        messages.success(self.request, 'Login URL copied successfully!')
        return redirect('login_detail', pk=self.object.pk)
        
    def copy_username(self):
        pyperclip.copy(self.object.username)
        messages.success(self.request, 'Username copied successfully!')
        return redirect('login_detail', pk=self.object.pk)
        
    def copy_password(self):
        pyperclip.copy(self.object.password)
        messages.success(self.request, 'Login Password copied successfully!')
        return redirect('login_detail', pk=self.object.pk)
    



@method_decorator(session_login_required, name='dispatch')
class LoginUpdateView(BaseVaultView, UserObjectMixin, UserFormValidMixin, UpdateView):
    model = Login
    form_class = LoginForm
    template_name = 'login_form.html'
    success_url = reverse_lazy('login_list')

    def form_valid(self, form):
        messages.success(self.request, 'Login item updated successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class LoginDeleteView(BaseVaultView, UserObjectMixin, DeleteView):
    model = Login
    template_name = 'login_confirm_delete.html'
    success_url = reverse_lazy('login_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Login item deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Views for CreditCard Data Type
@method_decorator(session_login_required, name='dispatch')
class CreditCardListView(BaseVaultView, ListView):
    model = CreditCard
    template_name = 'creditcard_list.html'
    context_object_name = 'creditcards'

    def get_queryset(self):
        user = self.session_manager.get_current_user()
        return CreditCard.objects.filter(user=user)

@method_decorator(session_login_required, name='dispatch')
class CreditCardCreateView(BaseVaultView, UserFormValidMixin, CreateView):
    model = CreditCard
    form_class = CreditCardForm
    template_name = 'creditcard_form.html'
    success_url = reverse_lazy('creditcard_list')

    def form_valid(self, form):
        form.instance.user = self.session_manager.get_current_user()
        messages.success(self.request, 'Credit card added successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class CreditCardDetailView(BaseVaultView, UserObjectMixin, DetailView):
    model = CreditCard
    template_name = 'creditcard_detail.html'
    context_object_name = 'creditcard'

@method_decorator(session_login_required, name='dispatch')
class CreditCardUpdateView(BaseVaultView, UserObjectMixin, UserFormValidMixin, UpdateView):
    model = CreditCard
    form_class = CreditCardForm
    template_name = 'creditcard_form.html'
    success_url = reverse_lazy('creditcard_list')

    def form_valid(self, form):
        messages.success(self.request, 'Credit card updated successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class CreditCardDeleteView(BaseVaultView, UserObjectMixin, DeleteView):
    model = CreditCard
    template_name = 'creditcard_confirm_delete.html'
    success_url = reverse_lazy('creditcard_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Credit card deleted successfully!')
        return super().delete(request, *args, **kwargs)


@method_decorator(session_login_required, name='dispatch')
class IdentityListView(BaseVaultView, ListView):
    model = Identity
    template_name = 'identity_list.html'
    context_object_name = 'identities'

    def get_queryset(self):
        user = self.session_manager.get_current_user()
        identities = Identity.objects.filter(user=user)

        today = date.today()
        upcoming_date = today + timedelta(days=30)  # Adjust the number of days as needed

        # Identify expired passports
        expired_passport_identities = identities.filter(
            passport_expiration_date__lt=today
        )

        # Identify passports expiring soon
        expiring_passport_identities = identities.filter(
            passport_expiration_date__gte=today,
            passport_expiration_date__lte=upcoming_date
        )

        # Identify expired licenses
        expired_license_identities = identities.filter(
            license_expiration_date__lt=today
        )

        # Identify licenses expiring soon
        expiring_license_identities = identities.filter(
            license_expiration_date__gte=today,
            license_expiration_date__lte=upcoming_date
        )

        # Combine the expired identities
        expired_identities = expired_passport_identities.union(expired_license_identities)

        # Combine the expiring identities
        expiring_identities = expiring_passport_identities.union(expiring_license_identities)

        # Notify mediator about expired items
        for identity in expired_identities:
            mediator.notify(
                sender="IdentityListView",
                event="identity_expired",
                data={
                    "user_id": identity.user.id,
                    "full_name": identity.full_name,
                    "passport_expiration_date": identity.passport_expiration_date,
                    "license_expiration_date": identity.license_expiration_date,
                },
            )

        # Notify mediator about expiring soon items
        for identity in expiring_identities:
            mediator.notify(
                sender="IdentityListView",
                event="identity_expiring_soon",
                data={
                    "user_id": identity.user.id,
                    "full_name": identity.full_name,
                    "passport_expiration_date": identity.passport_expiration_date,
                    "license_expiration_date": identity.license_expiration_date,
                },
            )

        # Add warning messages for expired items
        for expired_identity in expired_identities:
            if expired_identity.passport_expiration_date and expired_identity.passport_expiration_date < today:
                messages.warning(
                    self.request,
                    f"The passport for {expired_identity.full_name} has expired on {expired_identity.passport_expiration_date}. Please update it.",
                )
            if expired_identity.license_expiration_date and expired_identity.license_expiration_date < today:
                messages.warning(
                    self.request,
                    f"The license for {expired_identity.full_name} has expired on {expired_identity.license_expiration_date}. Please update it.",
                )

        # Add warning messages for expiring soon items
        for expiring_identity in expiring_identities:
            if expiring_identity.passport_expiration_date and today <= expiring_identity.passport_expiration_date <= upcoming_date:
                messages.warning(
                    self.request,
                    f"The passport for {expiring_identity.full_name} will expire on {expiring_identity.passport_expiration_date}. Please renew it soon.",
                )
            if expiring_identity.license_expiration_date and today <= expiring_identity.license_expiration_date <= upcoming_date:
                messages.warning(
                    self.request,
                    f"The license for {expiring_identity.full_name} will expire on {expiring_identity.license_expiration_date}. Please renew it soon.",
                )

        return identities



@method_decorator(session_login_required, name='dispatch')
class IdentityCreateView(BaseVaultView, UserFormValidMixin, CreateView):
    model = Identity
    form_class = IdentityForm
    template_name = 'identity_form.html'
    success_url = reverse_lazy('identity_list')

    def form_valid(self, form):        
        response = super().form_valid(form)

        # Log the identity creation for debugging
        print(f"Identity created: {form.instance.full_name} for user {form.instance.user.id}")        

        # Notify the mediator after Identity creation
        mediator.notify(
            sender="IdentityCreateView",
            event="identity_created",
            data={"user_id": form.instance.user.id, "full_name": form.instance.full_name},
        )
        messages.success(self.request, "Identity added successfully!")
        return response

@method_decorator(session_login_required, name='dispatch')
class IdentityDetailView(BaseVaultView, UserObjectMixin, DetailView):
    model = Identity
    template_name = 'identity_detail.html'
    context_object_name = 'identity'

@method_decorator(session_login_required, name='dispatch')
class IdentityUpdateView(BaseVaultView, UserObjectMixin, UserFormValidMixin, UpdateView):
    model = Identity
    form_class = IdentityForm
    template_name = 'identity_form.html'
    success_url = reverse_lazy('identity_list')

    def form_valid(self, form):
        messages.success(self.request, 'Identity updated successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class IdentityDeleteView(BaseVaultView, UserObjectMixin, DeleteView):
    model = Identity
    template_name = 'identity_confirm_delete.html'
    success_url = reverse_lazy('identity_list')

    def delete(self, request, *args, **kwargs):
        identity = self.get_object()
        messages.success(request, f'Identity for {identity.full_name} deleted successfully!')

        # Notify the mediator about the deletion
        mediator.notify(
            sender="IdentityDeleteView",
            event="identity_deleted",
            data={
                "user_id": identity.user.id,
                "full_name": identity.full_name,
            },
        )
        return super().delete(request, *args, **kwargs)
# Views for SecureNote Data Type
@method_decorator(session_login_required, name='dispatch')
class SecureNoteListView(BaseVaultView, ListView):
    model = SecureNote
    template_name = 'securenote_list.html'
    context_object_name = 'securenotes'

    def get_queryset(self):
        user = self.session_manager.get_current_user()
        return SecureNote.objects.filter(user=user)

@method_decorator(session_login_required, name='dispatch')
class SecureNoteCreateView(BaseVaultView, UserFormValidMixin, CreateView):
    model = SecureNote
    form_class = SecureNoteForm
    template_name = 'securenote_form.html'
    success_url = reverse_lazy('securenote_list')

    def form_valid(self, form):
        form.instance.user = self.session_manager.get_current_user()
        messages.success(self.request, 'Secure note added successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class SecureNoteDetailView(BaseVaultView, UserObjectMixin, DetailView):
    model = SecureNote
    template_name = 'securenote_detail.html'
    context_object_name = 'securenote'

@method_decorator(session_login_required, name='dispatch')
class SecureNoteUpdateView(BaseVaultView, UserObjectMixin, UserFormValidMixin, UpdateView):
    model = SecureNote
    form_class = SecureNoteForm
    template_name = 'securenote_form.html'
    success_url = reverse_lazy('securenote_list')

    def form_valid(self, form):
        messages.success(self.request, 'Secure note updated successfully!')
        return super().form_valid(form)

@method_decorator(session_login_required, name='dispatch')
class SecureNoteDeleteView(BaseVaultView, UserObjectMixin, DeleteView):
    model = SecureNote
    template_name = 'securenote_confirm_delete.html'
    success_url = reverse_lazy('securenote_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Secure note deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
