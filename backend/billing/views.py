from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer
from .models import Payment, Plan
from .serializers import PaymentSerializer, PlanSerializer


class PlanList(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.AllowAny]


class PromptPayInfo(APIView):
    """The PromptPay account to pay to (shown next to the QR on the frontend)."""
    permission_classes = [permissions.AllowAny]

    def get(self, _request):
        return Response({"promptpay_id": settings.PROMPTPAY_ID,
                         "promptpay_name": settings.PROMPTPAY_NAME})


class SubmitSlip(generics.CreateAPIView):
    """User uploads a PromptPay slip -> Payment(pending) for admin approval."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        plan = serializer.validated_data["plan"]
        serializer.save(user=self.request.user, amount=plan.price_thb)


class MySubscription(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        last = (Payment.objects.filter(user=request.user)
                .order_by("-created_at").first())
        return Response({
            "user": UserSerializer(request.user).data,
            "last_payment": PaymentSerializer(last).data if last else None,
        })
