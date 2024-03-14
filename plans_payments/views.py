from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from payments import RedirectNeeded, get_payment_model
from plans.models import Order


class PaymentDetailView(LoginRequiredMixin, View):
    login_url = reverse_lazy("auth_login")
    template_name = "plans_payments/payment.html"

    def get(self, request, *args, payment_id=None):
        payment = get_object_or_404(
            get_payment_model(), order__user=request.user, id=payment_id
        )
        try:
            form = payment.get_form(data=request.POST or None)
        except RedirectNeeded as redirect_to:
            payment.save()
            return redirect(str(redirect_to))
        return TemplateResponse(
            request, "plans_payments/payment.html", {"form": form, "payment": payment}
        )


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")


def create_payment_object(
    payment_variant, order, request=None, autorenewed_payment=False
):
    Payment = get_payment_model()
    if (
        hasattr(order.user.userplan, "recurring")
        and order.user.userplan.recurring.payment_provider != payment_variant
    ):
        order.user.userplan.recurring.delete()
    
    billing_info = order.user.billinginfo
    return Payment.objects.create(
        variant=payment_variant,
        order=order,
        description=f"{order.name} %s purchase",
        total=Decimal(order.total()),
        tax=Decimal(order.tax_total()),
        currency=order.currency,
        delivery=Decimal(0),
        billing_first_name=(billing_info.first_name or order.user.first_name),
        billing_last_name=(billing_info.last_name or order.user.last_name),
        billing_email=(billing_info.email or order.user.email),
        billing_address_1=billing_info.street,
        # billing_address_2=billing_info.zipcode,
        billing_city=billing_info.city,
        billing_postcode=billing_info.zipcode,
        billing_country_code=billing_info.country,
        # billing_country_area=billing_info.zipcode,
        customer_ip_address=get_client_ip(request) if request else "127.0.0.1",
        autorenewed_payment=autorenewed_payment,
    )


class CreatePaymentView(LoginRequiredMixin, View):
    login_url = reverse_lazy("auth_login")

    def get(self, request, *args, order_id=None, payment_variant=None):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        payment = create_payment_object(payment_variant, order, request)
        return redirect(reverse("payment_details", kwargs={"payment_id": payment.id}))
