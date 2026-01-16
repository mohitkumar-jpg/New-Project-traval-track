# gst.py
from django.utils import timezone
from django.db import models
from decimal import Decimal
import re
from django.db import transaction
from dashboards.branch.models.branch import Branch
from dashboards.super_admin.models.clients import SlabRate, Clients
from dashboards.super_admin.models.controll_no import DocumentControl, get_financial_year
from dashboards.super_admin.models.base import SoftDeleteModel ,FollowUp
from django.contrib.contenttypes.fields import GenericRelation


# ===============================
# ALL GST STATE MASTER
# ===============================
GST_STATE_MASTER = {
    "01": "Jammu & Kashmir",
    "02": "Himachal Pradesh",
    "03": "Punjab",
    "04": "Chandigarh",
    "05": "Uttarakhand",
    "06": "Haryana",
    "07": "Delhi",
    "08": "Rajasthan",
    "09": "Uttar Pradesh",
    "10": "Bihar",
    "11": "Sikkim",
    "12": "Arunachal Pradesh",
    "13": "Nagaland",
    "14": "Manipur",
    "15": "Mizoram",
    "16": "Tripura",
    "17": "Meghalaya",
    "18": "Assam",
    "19": "West Bengal",
    "20": "Jharkhand",
    "21": "Odisha",
    "22": "Chhattisgarh",
    "23": "Madhya Pradesh",
    "24": "Gujarat",
    "25": "Daman & Diu",
    "26": "Dadra & Nagar Haveli",
    "27": "Maharashtra",
    "29": "Karnataka",
    "30": "Goa",
    "31": "Lakshadweep",
    "32": "Kerala",
    "33": "Tamil Nadu",
    "34": "Puducherry",
    "35": "Andaman & Nicobar Islands",
    "36": "Telangana",
    "37": "Andhra Pradesh",
    "38": "Ladakh",
}

GST_UT_CODES = {"04", "07", "25", "26", "31", "34", "35", "38"}



def get_state_code_from_gstin(gstin):
    """
    GSTIN ke first 2 digit se state code nikalega
    """
    if not gstin:
        return None
    match = re.match(r"^(\d{2})", gstin)
    return match.group(1) if match else None



class Quotation(SoftDeleteModel):

    quotation_no = models.CharField( max_length=50, unique=True, blank=True)
    clients = models.ForeignKey(Clients,on_delete=models.PROTECT,related_name="quotations")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT ,blank=True, null=True)
    slab_rate = models.ForeignKey(SlabRate, on_delete=models.PROTECT ,blank=True, null=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft"
    )

    valid_till = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ FOLLOWUPS (GENERIC RELATION)
    followups = GenericRelation(FollowUp,related_query_name="quotation")

    def save(self, *args, **kwargs):
        if not self.quotation_no:
            with transaction.atomic():
                control = DocumentControl.objects.select_for_update().get(
                    company=self.company,
                    document_type="quotation",
                    financial_year=get_financial_year()
                )
                self.quotation_no = control.generate_document_number()

        super().save(*args, **kwargs)



class QuotationItem(SoftDeleteModel):

    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=255)

    quantity = models.PositiveIntegerField(default=1)

    rate = models.DecimalField(
        max_digits=10,
        decimal_places=4
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def save(self, *args, **kwargs):
        self.amount = Decimal(self.quantity) * Decimal(self.rate)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description




# ===============================
# GST INVOICE (RENAMED – NO CONFLICT)
# ===============================
class GSTInvoice(SoftDeleteModel):

    invoice_no = models.CharField( max_length=100,unique=True,blank=True)
    clients = models.ForeignKey(Clients,  on_delete=models.PROTECT, related_name="gst_invoices")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="gst_invoices")
    quotation = models.OneToOneField(Quotation, on_delete=models.PROTECT,related_name="gst_invoice")
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)

    # ================= GST =================
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    igst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=[
            ("unpaid", "Unpaid"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="unpaid"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ================= GST HELPERS =================

    def is_inter_state(self):
        company_state = get_state_code_from_gstin(self.company.gstin)
        branch_state = get_state_code_from_gstin(self.branch.gstin)
        return company_state and branch_state and company_state != branch_state

    def calculate_gst(self):
        gst_rate = Decimal("18.00")  # future: slab_rate based

        self.cgst_rate = self.sgst_rate = self.igst_rate = Decimal("0")
        self.cgst_amount = self.sgst_amount = self.igst_amount = Decimal("0")

        if self.is_inter_state():
            self.igst_rate = gst_rate
            self.igst_amount = self.sub_total * gst_rate / 100
        else:
            half = gst_rate / 2
            self.cgst_rate = half
            self.sgst_rate = half
            self.cgst_amount = self.sub_total * half / 100
            self.sgst_amount = self.sub_total * half / 100

        self.grand_total = (
            self.sub_total +
            self.cgst_amount +
            self.sgst_amount +
            self.igst_amount
        )

    def save(self, *args, **kwargs):

        # 🔥 AUTO INVOICE NUMBER (COMPANY + FY SAFE)
        if not self.invoice_no:
            with transaction.atomic():
                control = DocumentControl.objects.select_for_update().get(
                    company=self.company,
                    document_type="invoice",
                    financial_year=get_financial_year()
                )
                self.invoice_no = control.generate_document_number()

        # Subtotal from quotation items
        self.sub_total = sum(
            (item.amount for item in self.quotation.items.all()),
            Decimal("0.00")
        )

        self.calculate_gst()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_no
    



class Receipt(models.Model):

    RECEIPT_TYPES = [
        ("invoice", "Against Invoice"),
        ("advance", "Advance / On Account"),
        ("security", "Security Deposit"),
    ]

    PAYMENT_MODES = [
        ("cash", "Cash"),
        ("bank", "Bank"),
        ("upi", "UPI"),
        ("card", "Card"),
        ("cheque", "Cheque"),
    ]

    receipt_no = models.CharField(max_length=50, unique=True, blank=True)

    clients = models.ForeignKey(
        Clients,
        on_delete=models.PROTECT,
        related_name="receipts"
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="receipts"
    )

    receipt_type = models.CharField(
        max_length=20,
        choices=RECEIPT_TYPES
    )

    amount_received = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # --------------------
    # 🔹 TDS FIELDS
    # --------------------
    tds_applicable = models.BooleanField(default=False)

    tds_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    tds_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    unallocated_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES
    )

    reference_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

     # ✅ FOLLOWUPS (GENERIC RELATION)
    followups = GenericRelation(FollowUp,related_query_name="receipt")

    payment_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        # 🔹 Auto Receipt Number
        if not self.receipt_no:
            control = DocumentControl.objects.get(
                document_type="receipt",
                financial_year=get_financial_year()
            )
            self.receipt_no = control.generate_number()

        # 🔹 Calculate TDS
        if self.tds_applicable and self.tds_percentage:
            self.tds_amount = (
                self.amount_received * self.tds_percentage / Decimal("100")
            )
        else:
            self.tds_amount = Decimal("0.00")

        # 🔹 Net amount after TDS
        self.net_amount = self.amount_received - self.tds_amount

        # 🔹 Initially unallocated = net amount
        if not self.pk:
            self.unallocated_amount = self.net_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_no

class ReceiptAllocation(models.Model):

    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    invoice = models.ForeignKey(
        GSTInvoice,
        on_delete=models.PROTECT,
        related_name="receipt_allocations"
    )

    applied_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receipt.receipt_no} → {self.invoice.invoice_no}"

 
class ClientAdvanceLedger(models.Model):

    ENTRY_TYPES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    clients = models.ForeignKey(
        Clients,
        on_delete=models.PROTECT,
        related_name="advance_ledger"
    )

    receipt = models.ForeignKey(
        Receipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    invoice = models.ForeignKey(
        GSTInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    entry_type = models.CharField(
        max_length=10,
        choices=ENTRY_TYPES
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    narration = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.entry_type == "credit" else "-"
        return f"{self.clients} {sign}{self.amount}"
    

