from django.db import models
from decimal import Decimal
from django.forms import ValidationError
from dashboards.super_admin.models.base import SoftDeleteModel


class PurchaseOrder(SoftDeleteModel):
    party_master = models.ForeignKey(
        "PartyMaster",
        on_delete=models.CASCADE,
        related_name="purchase_orders"
    )
    po_number = models.CharField(max_length=100, unique=True)
    po_date = models.DateField()
    delivery_date = models.DateField()
    payment_terms = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        # ("received", "Received"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate * self.tax/100 + (self.quantity * self.rate)
        super().save(*args, **kwargs)




class GoodsReceiptNote(SoftDeleteModel):
    # purchase_order = models.ForeignKey(
    #     PurchaseOrder,
    #     on_delete=models.CASCADE,
    #     related_name="grn"
    # )
    purchase_order = models.OneToOneField(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="grn"
    )
    grn_number = models.CharField(max_length=100, unique=True)
    received_date = models.DateField()
    received_by = models.CharField(max_length=100)
    related_vehicle = models.CharField(max_length=100, blank=True, null=True)
    STATUS_CHOICES = [
        ("fully", "Fully Received"),
        ("partially", "Partially Received"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="partially")
    grn_status = models.CharField(
        max_length=20,
        choices=[("submitted", "Submitted"), ("sent", "Sent")],
        default="submitted"
    )