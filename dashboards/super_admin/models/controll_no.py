from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from dashboards.super_admin.models.base import SoftDeleteModel
from dashboards.super_admin.models.clients import Clients


# =====================================================
# DOCUMENT TYPES
# =====================================================
DOCUMENT_TYPES = [
    ("invoice", "Invoice"),
    ("quotation", "Quotation"),
    ("receipt", "Receipt"),
    ("dutySlip", "Duty Slip"),
    ("creditNote", "Credit Note"),
    ("debitNote", "Debit Note"),
    ("booking", "Booking"),
    ("payment", "Payment"),
    ("payout", "Payout"),
    ("purchaseOrder", "Purchase Order"),
    ("vendorBill", "Vendor Bill"),
    ("perfomaInvoice", "Performa Invoice"),
]


# =====================================================
# FINANCIAL YEAR HELPER
# =====================================================
def get_financial_year():
    """
    Financial year: April -> March
    Example: 2025-26
    """
    today = timezone.now().date()
    year = today.year

    if today.month < 4:
        return f"{year - 1}-{year}"
    return f"{year}-{year + 1}"


# =====================================================
# PREFIX / SUFFIX PLACEHOLDER PROCESSOR
# =====================================================
def process_affix(value, company, document_type, financial_year):
    """
    Replace dynamic placeholders in prefix / suffix
    """
    if not value:
        return None

    today = timezone.now().date()

    replacements = {
        "{FY}": financial_year,
        "{YYYY}": today.strftime("%Y"),
        "{YY}": today.strftime("%y"),
        "{MM}": today.strftime("%m"),
        "{COMP}": company.client_code,
        "{DOC}": document_type.upper(),
    }

    for key, val in replacements.items():
        value = value.replace(key, val)

    return value


# =====================================================
# DOCUMENT CONTROL MODEL
# =====================================================
class DocumentControl(SoftDeleteModel):
    """
    Company-wise + Document-wise + Financial-Year-wise
    document numbering controller
    """

    clients = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name="document_controls"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPES
    )

    prefix = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: INV, {DOC}, {COMP}, {FY}"
    )

    suffix = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Example: {FY}, {YYYY}"
    )

    start_number = models.PositiveIntegerField(default=1)
    current_number = models.PositiveIntegerField(default=0)

    number_padding = models.PositiveIntegerField(
        default=4,
        help_text="Digits count (0001 = 4)"
    )

    financial_year = models.CharField(
        max_length=9,
        default=get_financial_year,
        editable=False
    )

    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "clients",
            "document_type",
            "financial_year"
        )
        ordering = ["clients", "document_type"]
    def __str__(self):
        return (
            f"{self.company.display_name} | "
            f"{self.document_type.upper()} | "
            f"{self.financial_year}"
        )

    # =================================================
    # VALIDATION
    # =================================================
    def clean(self):
        if self.pk:
            old = DocumentControl.objects.get(pk=self.pk)
            if old.is_locked:
                raise ValidationError(
                    "This document series is locked and cannot be modified."
                )

    # =================================================
    # SAVE OVERRIDE
    # =================================================
    def save(self, *args, **kwargs):
        if self.current_number == 0:
            self.current_number = self.start_number - 1
        super().save(*args, **kwargs)

    # =================================================
    # GET NEXT RAW NUMBER (THREAD SAFE)
    # =================================================
    @transaction.atomic
    def get_next_number(self):
        """
        Returns only numeric padded value: 0001
        """
        if self.is_locked:
            raise ValidationError("This document series is locked.")

        self.current_number += 1
        self.save(update_fields=["current_number"])

        return str(self.current_number).zfill(self.number_padding)

    # =================================================
    # FULL DOCUMENT NUMBER GENERATOR
    # =================================================
    @transaction.atomic
    def generate_document_number(self):
        """
        Returns full formatted document number
        Example: INV/TCS/0001/2025-26
        """
        raw_number = self.get_next_number()

        prefix = process_affix(
            self.prefix,
            self.clients,
            self.document_type,
            self.financial_year
        )

        suffix = process_affix(
            self.suffix,
            self.clients,
            self.document_type,
            self.financial_year
        )

        parts = []
        if prefix:
            parts.append(prefix)

        parts.append(raw_number)

        if suffix:
            parts.append(suffix)

        return "/".join(parts)

    # =================================================
    # RESET FOR NEW FINANCIAL YEAR (OPTIONAL)
    # =================================================
    def reset_series(self):
        self.current_number = self.start_number - 1
        self.is_locked = False
        self.save()
