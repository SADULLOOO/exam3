from django.db import models
from accounts.models import User 
from django.utils import timezone
from datetime import timedelta

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    has_experience = models.BooleanField(default=False, verbose_name="Есть ли опыт?")
    cv_file = models.FileField(upload_to='cv_uploads/', blank=True, null=True, verbose_name="Файл CV")
    applied_for_license = models.BooleanField(default=False) # Подал ли заявку

    def __str__(self):
        return f"{self.user.username}"


class License(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='license')
    license_key = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    price_per_month = models.DecimalField(max_digits=12, decimal_places=2, default=15000.00)

    def check_and_update_price(self):
        if timezone.now() > self.created_at + timedelta(days=180):
            self.price_per_month = 25000.00
            self.save()
        return self.price_per_month

    def __str__(self):
        return f"License {self.license_key} for {self.user.username} (Active: {self.is_active})"