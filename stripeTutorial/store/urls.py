from django.urls import path
from .views import (
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    # ProductLandingPageView,
    stripe_webhook,
    StripeIntentView,
    CustomPaymentView,
    ProductListView,
    PriceListView,
    PriceDetailView
)

urlpatterns = [
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<pk>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    # path('', ProductLandingPageView.as_view(), name='landing'),
    path("", ProductListView.as_view(),name="product-list"),
    path("price/", PriceListView.as_view(),name="price-list"),
    path("price/<int:pk>/", PriceDetailView.as_view(), name="price-detail"),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(), name='create-payment-intent'),
    path('custom-payment/', CustomPaymentView.as_view(), name='custom-payment'),
]