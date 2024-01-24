import stripe
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from .models import Price

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        # Update domain after site is hosted
        domain = "http://127.0.0.1:8000"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        # Pass in parameters to the Stripe checkout function
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price': price.stripe_price_id,
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=domain + '/success/',
            cancel_url=domain + '/cancel/',
        )
        return redirect(checkout_session.url)
    
class SuccessView(TemplateView):
    template_name = "success.html"

class CancelView(TemplateView):
    template_name = "cancel.html"