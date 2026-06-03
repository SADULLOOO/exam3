from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Credit

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status == 'paid':
        print(f"🔥 Signals works! Order №{instance.id} succesfull added!")