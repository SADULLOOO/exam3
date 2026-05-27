from django.db import models
from django.conf import settings


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True
    )

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
    
class Credit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    months = models.IntegerField()

    interest_rate = models.FloatField(default=12.5) 

    created_at = models.DateTimeField(auto_now_add=True)