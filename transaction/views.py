from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Transaction
from user.models import User  # Ensure your custom User model is properly referenced
from .paystack import initialize_transaction, verify_transaction
from .serializers import PaystackPaymentSerializer, TransactionSerializer
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class PaystackPaymentInitView(APIView):
    """Initialize Paystack Payment"""

    def post(self, request):
        serializer = PaystackPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        amount = serializer.validated_data["amount"]
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        # Call Paystack API to initialize transaction
        try:
            response = initialize_transaction(email, amount)

            if response.get("status"):
                transaction = Transaction.objects.create(
                    user=user,
                    reference=response["data"]["reference"],
                    amount=amount,
                    status="pending"
                )

                return Response({
                    "message": "Transaction initialized",
                    "authorization_url": response["data"]["authorization_url"],  # Send this to frontend
                    "transaction": TransactionSerializer(transaction).data
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "Paystack transaction initialization failed",
                "details": response
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error initializing Paystack transaction: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def initialize_payment_view(request):
    """Function-based view to initialize Paystack payment"""

    serializer = PaystackPaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid request data", "details": serializer.errors}, status=400)

    email = serializer.validated_data["email"]
    amount = serializer.validated_data["amount"]

    try:
        response = initialize_transaction(email, amount)
        if response.get("status"):
            logger.info(f"Paystack transaction initialized for {email}")
            return JsonResponse(response, status=200)

        logger.warning(f"Failed to initialize transaction for {email}: {response}")
        return JsonResponse({"error": "Paystack transaction failed", "details": response}, status=400)

    except Exception as e:
        logger.error(f"Error initializing transaction: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@api_view(["GET"])
def verify_payment_view(request, reference):
    """Verify Paystack Payment and Update Transaction Status"""

    transaction = get_object_or_404(Transaction, reference=reference)

    try:
        response = verify_transaction(reference)  # Call Paystack API to verify transaction

        if response.get("status") and response["data"]["status"] == "success":
            transaction.status = "success"
            transaction.save()
            return Response({
                "message": "Payment verified successfully",
                "transaction": TransactionSerializer(transaction).data
            }, status=status.HTTP_200_OK)

        transaction.status = "failed"
        transaction.save()
        return Response({
            "error": "Payment verification failed",
            "details": response
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error verifying transaction {reference}: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def paystack_webhook(request):
    """Handle Paystack Webhook Events"""
    try:
        data = request.data
        event = data.get("event")

        if event == "charge.success":
            reference = data["data"]["reference"]
            transaction = Transaction.objects.filter(reference=reference).first()

            if transaction:
                transaction.status = "success"
                transaction.save()
                logger.info(f"Transaction {reference} marked as successful via webhook")
            else:
                logger.warning(f"Webhook received for unknown transaction reference: {reference}")

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error handling Paystack webhook: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
