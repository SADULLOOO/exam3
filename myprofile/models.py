from django.db import models
from accounts.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/')

    def __str__(self):
        return f"{self.user.username}"
# Create your models here.
