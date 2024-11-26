from django.contrib import admin
from django.contrib.auth.models import User
from .models import Login, CreditCard, Identity, SecureNote

admin.site.register(Login)
admin.site.register(CreditCard)
admin.site.register(Identity)
admin.site.register(SecureNote)
