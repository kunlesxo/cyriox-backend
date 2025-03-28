from rest_framework import generics, permissions, viewsets, filters
from rest_framework.exceptions import PermissionDenied
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProductCategory, Product, Order, OrderItem, Invoice, Cart, CartItem, StockInventory,SalesRecord
from .serializers import (
    ProductCategorySerializer, ProductSerializer,
    OrderSerializer, OrderItemSerializer, InvoiceSerializer,
    CartSerializer, CartItemSerializer, StockInventorySerializer, SalesRecordSerializer
)
from rest_framework import generics
from rest_framework.response import Response

class SalesAnalyticsView(generics.ListAPIView):
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SalesRecord.objects.filter(distributor=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        total_sales = queryset.aggregate(total_sales=Sum("total_sales"))["total_sales"] or 0
        total_revenue = queryset.aggregate(total_revenue=Sum("revenue"))["total_revenue"] or 0
        
        return Response({
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "sales_records": SalesRecordSerializer(queryset, many=True).data
        })

# Product Category Views
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    
# Product Views
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['category', 'distributor']

    def get_queryset(self):
        return Product.objects.filter(distributor=self.request.user)

    def perform_create(self, serializer):
        serializer.save(distributor=self.request.user)

# Order Views
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['customer_name', 'status']
    filterset_fields = ['status']

    def get_queryset(self):
        return Order.objects.filter(distributor=self.request.user).select_related('distributor')

    def perform_update(self, serializer):
        order = serializer.instance
        if order.distributor != self.request.user:
            raise PermissionDenied("You do not have permission to modify this order.")

        new_status = self.request.data.get("status")
        if new_status == "paid" and not hasattr(order, 'invoice'):
            Invoice.objects.create(
                order=order,
                invoice_number=f"INV-{order.id:06d}",
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=30),
                total_amount=sum(item.price * item.quantity for item in order.items.all()),
                payment_status="paid",
                payment_method=self.request.data.get("payment_method", "card")
            )
        serializer.save()

# Order Item Views
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__distributor=self.request.user).select_related('product', 'order')

# Invoice Views
class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(order__distributor=self.request.user).select_related('order')

# Cart Views
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user)

# Cart Item Views
class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__customer=self.request.user).select_related('product', 'cart')

    def perform_create(self, serializer):
        cart = serializer.validated_data['cart']
        product = serializer.validated_data['product']
        if cart.items.exists():
            existing_distributor = cart.items.first().product.distributor
            if existing_distributor != product.distributor:
                raise PermissionDenied("You can only add products from the same distributor to your cart.")
        serializer.save()

# Stock Inventory Views
class StockInventoryViewSet(viewsets.ModelViewSet):
    queryset = StockInventory.objects.all().order_by('-timestamp')
    serializer_class = StockInventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'action']
