from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.account, name='account'),
    path('login/', views.login_view, name='login'),
    path('vault/', views.vault, name='vault'),
    path('create-password/', views.create_password, name='create_password'),
    path('register/', views.register, name='register'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('enter-username/', views.enter_username, name='enter_username'),
    path('password-reset/', views.password_reset, name='password_reset'),
]