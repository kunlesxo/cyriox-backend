from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount in percentage")
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    distributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def discounted_price(self):
        """Calculate the price after discount."""
        return self.price * (1 - self.discount / 100)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    distributor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    tracking_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = get_random_string(12).upper()
        super().save(*args, **kwargs)

        # Generate an invoice automatically when the order is marked as paid
        if self.payment_status == "paid" and not hasattr(self, "invoice"):
            Invoice.objects.create(
                order=self,
                invoice_number=f"INV-{self.id}-{timezone.now().strftime('%Y%m%d')}",
                issue_date=timezone.now(),
                due_date=timezone.now() + timedelta(days=30),
                payment_status="paid",
            )

    def __str__(self):
        return f"Order {self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product.stock >= self.quantity:
            self.product.stock -= self.quantity
            self.product.save()
        else:
            raise ValueError("Not enough stock available")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

class Invoice(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack'),
        ('paypal', 'PayPal'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue')],
        default='pending'
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='card')

    def save(self, *args, **kwargs):
        """Calculate the total amount from order items before saving."""
        self.total_amount = sum(item.price * item.quantity for item in self.order.items.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.id}"

class Cart(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} - {self.customer.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"
    
class StockInventory(models.Model):
    STOCK_ACTIONS = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    action = models.CharField(max_length=20, choices=STOCK_ACTIONS)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action.capitalize()} - {self.quantity} {self.product.name}"
    
class SalesRecord(models.Model):
    distributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Sales for {self.distributor.username} on {self.date}"


