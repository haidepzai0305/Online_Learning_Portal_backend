from django.urls import path
from .views import (
    create_checkout_session_view,
    payment_webhook_view,
    list_my_transactions_view
)

urlpatterns = [
    path('checkout/', create_checkout_session_view, name='create-checkout'),
    path('webhook/', payment_webhook_view, name='payment-webhook'),
    path('history/', list_my_transactions_view, name='payment-history'),
]
