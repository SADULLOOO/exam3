from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Credit

@receiver(post_save, sender=Order)
def update_car_status_order(sender, instance, created, **kwargs):
    if instance.status == 'paid':
        car = instance.car
        car.is_available = False
        car.save()

@receiver(post_save, sender=Credit)
def update_car_status_credit(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        car = instance.car
        car.is_available = False
        car.save()