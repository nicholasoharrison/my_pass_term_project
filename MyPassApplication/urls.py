from django.urls import path
from . import views

urlpatterns = [
    path('', views.account, name='account'),
    path('login/', views.login_view, name='login'),
    path('vault/', views.vault, name='vault'),
    path('create-password/', views.create_password, name='create_password'),
    path('register/', views.register, name='register'),
]