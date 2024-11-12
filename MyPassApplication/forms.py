from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Account, SecurityQuestion

class CustomUserCreationForm(UserCreationForm):
    q1Answer = forms.CharField(label="What is your favorite color?", max_length=100)
    q2Answer = forms.CharField(label="What city were you born in?", max_length=100)
    q3Answer = forms.CharField(label="What is the name of your first employer?", max_length=100)

    email = forms.EmailField(required=True)

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

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

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

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        warnings = []
        if len(password1) < 8:
            raise forms.ValidationError("The password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("This password is entirely numeric.")
        if not any(char.isalpha() for char in password1):
            raise forms.ValidationError("The password must contain at least one letter.")
        if warnings:
            for warning in warnings:
                self.add_error('password1', warning)
        else:
              self.add_error('password1', "You must enter a password.")
        return password1



class SecurityQuestionForm(forms.Form):
    answer = forms.CharField(
        label='Answer', 
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter your answer'})
    )



class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Enter your username')


class EditPasswordForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'password']
