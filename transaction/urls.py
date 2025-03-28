from django.urls import path
from .views import (
    initialize_payment_view,
    PaystackPaymentInitView,
    verify_payment_view
)

urlpatterns = [
    # Function-based view for initializing payment
    path("paystack/init/", initialize_payment_view, name="paystack-initialize"),

    # Class-based view for initializing payment
    path("paystack/init-class/", PaystackPaymentInitView.as_view(), name="paystack-initialize-class"),

    # Payment verification endpoint
    path("paystack/verify/<str:reference>/", verify_payment_view, name="paystack-verify"),
]
