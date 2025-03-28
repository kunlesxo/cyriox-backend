from django.urls import path
from .views import (
    ProductCategoryViewSet, ProductViewSet, OrderViewSet,
    OrderItemViewSet, InvoiceViewSet, CartViewSet,
    CartItemViewSet, StockInventoryViewSet, SalesAnalyticsView
)

urlpatterns = [
    # Product Categories
    path('categories/', ProductCategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list-create'),
    path('categories/<int:pk>/', ProductCategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='category-detail'),

    # Products
    path('products/', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list-create'),
    path('products/<int:pk>/', ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='product-detail'),

    # Orders
    path('orders/', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list-create'),
    path('orders/<int:pk>/', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-detail'),

    # Order Items
    path('order-items/', OrderItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-item-list-create'),
    path('order-items/<int:pk>/', OrderItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-item-detail'),

    # Invoices (ReadOnly)
    path('invoices/', InvoiceViewSet.as_view({'get': 'list'}), name='invoice-list'),
    path('invoices/<int:pk>/', InvoiceViewSet.as_view({'get': 'retrieve'}), name='invoice-detail'),

    # Carts
    path('carts/', CartViewSet.as_view({'get': 'list', 'post': 'create'}), name='cart-list-create'),
    path('carts/<int:pk>/', CartViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='cart-detail'),

    # Cart Items
    path('cart-items/', CartItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='cart-item-list-create'),
    path('cart-items/<int:pk>/', CartItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='cart-item-detail'),

    # Stock Inventory
    path('stock-inventory/', StockInventoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='stock-inventory-list'),
    path('stock-inventory/<int:pk>/', StockInventoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='stock-inventory-detail'),

    path("sales/", SalesAnalyticsView.as_view(), name="sales_analytics"),
]
