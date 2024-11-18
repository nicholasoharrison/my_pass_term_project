from django.shortcuts import redirect
from django.urls import path

from .vault_views import (
    LoginListView, LoginCreateView, LoginDetailView, LoginUpdateView, LoginDeleteView,
    CreditCardListView, CreditCardCreateView, CreditCardDetailView, CreditCardUpdateView, CreditCardDeleteView,
    IdentityListView, IdentityCreateView, IdentityDetailView, IdentityUpdateView, IdentityDeleteView,
    SecureNoteListView, SecureNoteCreateView, SecureNoteDetailView, SecureNoteUpdateView, SecureNoteDeleteView,
)
from . import views

urlpatterns = [
    # Authentication and Account Management
    path('', views.account, name='account'),
    path('login/', views.login_view, name='login'),
    path('create-password/', views.create_password, name='create_password'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset via Security Questions
    path('enter-username/', views.enter_username, name='enter_username'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('password-reset/', views.password_reset, name='password_reset'),
   # path('delete_password/<int:password_id>/', views.delete_password, name='delete_password'),

    # Vault Home
    path('vault/', views.vault, name='vault_home'),

    # Notification URL
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),

    # Login URLs
    path('vault/logins/', LoginListView.as_view(), name='login_list'),
    path('vault/logins/new/', LoginCreateView.as_view(), name='login_create'),
    path('vault/logins/<int:pk>/', LoginDetailView.as_view(), name='login_detail'),
    path('vault/logins/<int:pk>/edit/', LoginUpdateView.as_view(), name='login_edit'),
    path('vault/logins/<int:pk>/delete/', LoginDeleteView.as_view(), name='login_delete'),

    # Credit Card URLs
    path('vault/creditcards/', CreditCardListView.as_view(), name='creditcard_list'),
    path('vault/creditcards/new/', CreditCardCreateView.as_view(), name='creditcard_create'),
    path('vault/creditcards/<int:pk>/', CreditCardDetailView.as_view(), name='creditcard_detail'),
    path('vault/creditcards/<int:pk>/edit/', CreditCardUpdateView.as_view(), name='creditcard_edit'),
    path('vault/creditcards/<int:pk>/delete/', CreditCardDeleteView.as_view(), name='creditcard_delete'),

    # Identity URLs
    path('vault/identities/', IdentityListView.as_view(), name='identity_list'),
    path('vault/identities/new/', IdentityCreateView.as_view(), name='identity_create'),
    path('vault/identities/<int:pk>/', IdentityDetailView.as_view(), name='identity_detail'),
    path('vault/identities/<int:pk>/edit/', IdentityUpdateView.as_view(), name='identity_edit'),
    path('vault/identities/<int:pk>/delete/', IdentityDeleteView.as_view(), name='identity_delete'),

    # Secure Note URLs
    path('vault/securenotes/', SecureNoteListView.as_view(), name='securenote_list'),
    path('vault/securenotes/new/', SecureNoteCreateView.as_view(), name='securenote_create'),
    path('vault/securenotes/<int:pk>/', SecureNoteDetailView.as_view(), name='securenote_detail'),
    path('vault/securenotes/<int:pk>/edit/', SecureNoteUpdateView.as_view(), name='securenote_edit'),
    path('vault/securenotes/<int:pk>/delete/', SecureNoteDeleteView.as_view(), name='securenote_delete'),
]