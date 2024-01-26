from typing import Any
import stripe, json
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Price, Product

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

# Stripe Checkout page (low-code)
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

# class ProductLandingPageView(TemplateView):
#     template_name = "landing.html"

#     def get_context_data(self, **kwargs):
#         products = Product.objects.all()
#         # prices = Price.objects.filter(product=product)
#         context = super(ProductLandingPageView, self).get_context_data(**kwargs)
#         context.update({
#             "product": product,
#             "prices": prices
#         })
#         return context
    
class ProductListView(ListView):
    model = Product

class PriceListView(ListView):
    model = Price

class PriceDetailView(DetailView):
    model = Price

# Stripe webhook event handler (to validate payment)
# csrf exempt bc Stripe sends the POST request w/o token, which is normally required by Django
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    # Verify Stripe sent the webhook
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        # payment_intent = session["payment_intent"]
        line_items = stripe.checkout.Session.list_line_items(session["id"])

        # Grabs first line item since there is only one
        stripe_price_id = line_items["data"][0]["price"]["id"]
        price = Price.objects.get(stripe_price_id=stripe_price_id)
        product = price.product

        # Send email to customer
        # My email is not configured to grant Django access
        send_mail(
            subject="Purchase complete",
            message="Thanks for shopping!",
            recipient_list=[customer_email],
            from_email="caitlinfcorrigan@gmail.com"
        )
    elif event["type"] == "payment_intent.succeeded":
        intent = event['data']['object']

        stripe_customer_id = intent['customer']
        stripe_customer = stripe.Customer.retrieve(stripe_customer_id)

        customer_email = stripe_customer['email']
        price_id = intent['metadata']['price_id']

        price = Price.objects.get(id=price_id)
        product = price.product

        send_mail(
            subject="Purchase complete",
            message="Thanks for shopping!",
            recipient_list=[customer_email],
            from_email="caitlinfcorrigan@gmail.com"
        )
        
    return HttpResponse(status=200)

class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            customer = stripe.Customer.create(email=req_json['email'])
            price = Price.objects.get(id=self.kwargs["pk"])
            intent = stripe.PaymentIntent.create(
                amount=price.price,
                currency='usd',
                customer=customer['id'],
                metadata={
                    "price_id": price.id
                }
            )
            return JsonResponse({
                "clientSecret": intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})
        

class CustomPaymentView(TemplateView):
    template_name = "custom_payment.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Test Product")
        prices = Price.objects.filter(product=product)
        context = super(CustomPaymentView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "prices": prices,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context
    
def custom_payment(request):
    # Select from Price as it has the FK
    products = Price.objects.select_related('product').all()
    return render(request, 'cust_pay.html', {"products":products, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY})

