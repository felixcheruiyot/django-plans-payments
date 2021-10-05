from django.contrib import admin

from related_admin import RelatedFieldAdmin

from . import models


@admin.register(models.Payment)
class PaymentAdmin(RelatedFieldAdmin):
    list_display = (
        'id',
        'transaction_id',
        'token',
        'order__user',
        'variant',
        'status',
        'fraud_status',
        'currency',
        'total',
        'customer_ip_address',
        'tax',
        'transaction_fee',
        'captured_amount',
        'created',
        'modified',
        'autorenewed_payment',
    )
    list_filter = (
        'status',
        'variant',
        'fraud_status',
        'currency',
        'autorenewed_payment',
    )
    search_fields = (
        'order__user__first_name',
        'order__user__last_name',
        'order__user__email',
        'transaction_id',
        'extra_data',
        'token',
    )
    list_select_related = (
        'order__user',
    )
    readonly_fields = (
        'created',
        'modified',
    )
