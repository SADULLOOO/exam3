from django.contrib import admin
from .models import User, PasswordReset, EmailConfirm

admin.site.register(User)
# Register your models here.
