from rest_framework import serializers
from .models import ProductCategory, Product, Order, OrderItem, Invoice, Cart, CartItem, StockInventory,SalesRecord


class SalesRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRecord
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'quantity', 'added_at']

    def validate(self, data):
        """Ensure cart items do not exceed available stock."""
        product = data.get('product')
        if product.stock < data.get('quantity'):
            raise serializers.ValidationError(f"Only {product.stock} units available.")
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'created_at']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'discount',
            'discounted_price', 'stock', 'category', 'distributor',
            'created_at', 'updated_at'
        ]

    def get_discounted_price(self, obj):
        """Calculate the final price after discount."""
        return obj.price * (1 - obj.discount / 100)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'price']

    def validate(self, data):
        """Ensure there is enough stock before adding order items."""
        product = data.get('product')
        if product.stock < data.get('quantity'):
            raise serializers.ValidationError(f"Only {product.stock} units available.")
        return data

    def create(self, validated_data):
        """Deduct stock when an order item is created."""
        product = validated_data['product']
        product.stock -= validated_data['quantity']
        product.save()
        return super().create(validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.ReadOnlyField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'distributor', 'customer_name', 'customer_email', 'status',
            'tracking_number', 'estimated_delivery', 'created_at', 'updated_at',
            'items', 'total_amount'
        ]

    def get_total_amount(self, obj):
        """Calculate total order amount."""
        return sum(item.price * item.quantity for item in obj.items.all())

    def update(self, instance, validated_data):
        """Generate an invoice if order status is marked as 'paid' and restore stock if canceled."""
        previous_status = instance.status
        instance = super().update(instance, validated_data)

        new_status = validated_data.get("status", instance.status)
        
        if new_status == 'paid' and previous_status != 'paid':
            if not Invoice.objects.filter(order=instance).exists():
                Invoice.objects.create(
                    order=instance,
                    invoice_number=f'INV-{instance.id:06d}',
                    due_date=instance.created_at.date(),
                    total_amount=self.get_total_amount(instance),
                    payment_status='paid',
                    payment_method='card'
                )
        
        if new_status == 'canceled' and previous_status != 'canceled':
            for item in instance.items.all():
                item.product.stock += item.quantity
                item.product.save()
        
        return instance


class InvoiceSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(source='order', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'order_id', 'invoice_number', 'issue_date', 'due_date',
            'total_amount', 'payment_status', 'payment_method'
        ]


class StockInventorySerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = StockInventory
        fields = ['id', 'product', 'product_name', 'action', 'quantity', 'timestamp', 'description']

    def create(self, validated_data):
        """Automatically update stock when a stock movement is recorded."""
        product = validated_data['product']
        action = validated_data['action']
        quantity = validated_data['quantity']

        if action == 'restock':
            product.stock += quantity
        elif action in ['sale', 'return', 'adjustment']:
            if product.stock < quantity:
                raise serializers.ValidationError(f"Not enough stock available for {product.name}.")
            product.stock -= quantity
        
        product.save()
        return super().create(validated_data)



