from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    ProductLandingPageView,
    stripe_webhook
)

urlpatterns = [
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('', ProductLandingPageView.as_view(), name='landing'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
]