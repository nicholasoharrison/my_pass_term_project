from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Account, SecurityQuestion, Login, CreditCard, Identity, SecureNote

class CustomUserCreationForm(UserCreationForm):
    q1Answer = forms.CharField(label="What is your favorite color?", max_length=100)
    q2Answer = forms.CharField(label="What city were you born in?", max_length=100)
    q3Answer = forms.CharField(label="What is the name of your first employer?", max_length=100)

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            SecurityQuestion.objects.create(
                user=user,
                q1Answer=self.cleaned_data.get('q1Answer'),
                q2Answer=self.cleaned_data.get('q2Answer'),
                q3Answer=self.cleaned_data.get('q3Answer'),
            )
        return user
    
    #fixing doubled or error messages
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Remove default password validators
        self.fields['password1'].validators = []
        self.fields['password2'].validators = []

   

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        if not username.isalnum():
            raise forms.ValidationError("The username should only contain letters and numbers.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    # This approach prevents the user from registering if the password is weak.

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        warnings = []
        if len(password1) < 8:
            warnings.append("Your password is less than 8 characters long.")
        if not any(char.isdigit() for char in password1):
            warnings.append("Your password is entirely numeric.")
        if not any(char.isalpha() for char in password1):
            warnings.append("The password must contain at least one letter.")
        if warnings:
            # Store warnings in the form's non-field errors
            self.add_error('password1', 'Weak password:')
            for warning in warnings:
                self.add_error('password1', warning)
        return password1
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        return cleaned_data




class SecurityQuestionForm(forms.Form):
    answer = forms.CharField(
        label='Answer', 
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your answer'})
    )



class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Enter your username')

class LoginForm(forms.ModelForm):
    class Meta:
        model = Login
        fields = ['site_name', 'site_url', 'username', 'password', 'notes']

class CreditCardForm(forms.ModelForm):
    class Meta:
        model = CreditCard
        fields = ['cardholder_name', 'card_number', 'expiration_date', 'cvv', 'billing_address']

class IdentityForm(forms.ModelForm):
    class Meta:
        model = Identity
        fields = ['full_name', 'date_of_birth', 'passport_number', 'license_number', 'social_security_number', 'notes']

class SecureNoteForm(forms.ModelForm):
    class Meta:
        model = SecureNote
        fields = ['title', 'content']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'password']        