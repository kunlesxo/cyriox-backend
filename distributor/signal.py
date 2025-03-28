from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Order, Invoice

@receiver(post_save, sender=Order)
def create_invoice(sender, instance, created, **kwargs):
    """
    Generate an invoice when an order is marked as 'paid' and doesn't already have one.
    """
    if instance.status == 'paid' and not hasattr(instance, 'invoice'):
        Invoice.objects.create(
            order=instance,
            invoice_number=f"INV-{instance.id:06d}",  # Ensures a 6-digit invoice format
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),  # 30-day due period
            total_amount=sum(item.price * item.quantity for item in instance.items.all()),  # Ensure amount is stored
            payment_status='paid',
            payment_method=getattr(instance, 'payment_method', 'card')  # Handle missing payment_method field
        )
