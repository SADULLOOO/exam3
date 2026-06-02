from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class NonDeletedBrandManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Brand(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='my_brands',
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    objects = NonDeletedBrandManager() 
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.owner_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            self.owner = User.objects.filter(is_superuser=True).first()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CarModel(models.Model):

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='models'
    )

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class Car(models.Model):

    STATUS_CHOICES = (
        ('new', 'New'),
        ('used', 'Used'),
        ('damaged', 'Damaged'),
    )

    TRANSMISSION_CHOICES = (
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    )

    FUEL_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    )

    model = models.ForeignKey(
        CarModel,
        on_delete=models.CASCADE,
        related_name='cars'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.owner_id:
            self.owner = User.objects.filter(is_superuser=True).first()
        super().save(*args, **kwargs)

    title = models.CharField(max_length=255)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    year = models.PositiveIntegerField()

    mileage = models.PositiveIntegerField()

    engine = models.CharField(max_length=100)

    engine_volume = models.FloatField()

    horsepower = models.PositiveIntegerField()

    color = models.CharField(max_length=50)

    country = models.CharField(max_length=100)

    transmission = models.CharField(
        max_length=20,
        choices=TRANSMISSION_CHOICES
    )

    fuel_type = models.CharField(
        max_length=20,
        choices=FUEL_CHOICES
    )

    hybrid = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    description = models.TextField()

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CarImage(models.Model):

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='cars/')

    def __str__(self):
        return f"Image for {self.car.title}"


class Favorite(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.car.title}"


class Review(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    text = models.TextField()

    stars = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review"


class OrderRequest(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=30)

    message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order by {self.user.username}"
    

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivering', 'Delivering'),
        ('done', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    car = models.ForeignKey(
        'Car',
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    delivery_date = models.DateTimeField(
        default=timezone.now() + timedelta(days=7)
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

class Credit(models.Model):

    STATUS_CHOICES = [
        ('processing','Processing'),
        ('approved','Approved'),
        ('cancelled','Cancelled')
    ]

    user=models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    car=models.ForeignKey(
        Car,
        on_delete=models.CASCADE
    )

    amount=models.IntegerField()

    months=models.IntegerField()

    status=models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='processing'
    )

class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    last_login_time = models.DateTimeField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    total_seconds = models.IntegerField(default=0)


class Conversation(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_conversations')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('buyer', 'car')


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    text = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

class AIChatHistory(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
        user_message = models.TextField()  
        ai_response = models.TextField()   
        timestamp = models.DateTimeField(auto_now_add=True)  

        def __str__(self):
            return f"Chat by {self.user.username} at {self.timestamp}"