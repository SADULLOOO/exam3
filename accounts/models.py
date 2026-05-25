from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=14, null=True)
    photo = models.ImageField(upload_to='users/', null=True, blank=True)

    def __str__(self):
        return f'{self.email} --> {self.username} --> {self.phone}'
    
class EmailConfirm(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username

class PasswordReset(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return self.user.username  


# Create your models here.
