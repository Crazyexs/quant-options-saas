from django.urls import path

from .views import MySubscription, PlanList, PromptPayInfo, SubmitSlip

urlpatterns = [
    path("plans/", PlanList.as_view(), name="plans"),
    path("promptpay/", PromptPayInfo.as_view(), name="promptpay-info"),
    path("promptpay/submit/", SubmitSlip.as_view(), name="promptpay-submit"),
    path("subscription/", MySubscription.as_view(), name="subscription"),
]
