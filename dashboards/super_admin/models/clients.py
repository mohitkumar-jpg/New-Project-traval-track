# billing.py
from django.db import models
from django.core.exceptions import ValidationError
from dashboards.super_admin.models.base import Location, SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation



# start slab rate 

BILLING_MODES = [
    ("per_duty_slip", "Per Duty Slip"),
    ("flat", "Flat"),
    ("local_sms", "Local SMS"),
    ("international_sms", "International SMS"),
    ("local_whatsapp", "Local WhatsApp"),
    ("international_whatsapp", "International WhatsApp"),
    ("e_invoice", "E-Invoice"),
    ("email", "Email"),
]

PRICE_TYPES = [
    ("per_unit", "Per Unit Price"),
    ("fixed", "Fixed Price"),
]

MONTH_CHOICES = [
    (1, "1 Month"),
    (3, "3 Months"),
    (6, "6 Months"),
    (12, "12 Months"),
]


class SlabRate(SoftDeleteModel):
    slab_name = models.CharField(max_length=100)

    billing_mode = models.CharField(
        max_length=30,
        choices=BILLING_MODES
    )

    price_type = models.CharField(
        max_length=20,
        choices=PRICE_TYPES,
        blank=True,
        null=True
    )

    min_qty = models.PositiveIntegerField(blank=True, null=True)
    max_qty = models.PositiveIntegerField(blank=True, null=True)

    months = models.PositiveIntegerField(
        choices=MONTH_CHOICES,
        blank=True,
        null=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.billing_mode == "per_duty_slip":
            if not self.price_type:
                raise ValidationError("Price type required")
            if self.min_qty is None or self.max_qty is None:
                raise ValidationError("Min & Max qty required")
            self.months = None

        elif self.billing_mode == "flat":
            if not self.months:
                raise ValidationError("Months required")
            self.price_type = None
            self.min_qty = None
            self.max_qty = None

        else:
            if not self.price_type:
                raise ValidationError("Price type required")
            self.min_qty = None
            self.max_qty = None
            self.months = None

    def __str__(self):
        return f"{self.slab_name} | {self.billing_mode}"


# Create Clinets profile dashbord
class Clients(SoftDeleteModel):
    CLIENT_TYPES = [
    ('corporate', 'Corporate'),
    ('ets', 'ETS'),
    ('spot', 'Spot'),
    ('selfdrive', 'Self Drive'),
]

    display_name = models.CharField(max_length=200)
    legal_company_name = models.CharField(max_length=200, blank=True, null=True)
    client_code = models.CharField(max_length=50, unique=True)
    client_type = models.CharField(max_length=20, choices=CLIENT_TYPES, default='corporate')
    industry = models.CharField(max_length=200, blank=True, null=True)
    timezone = models.CharField(max_length=100, default='Asia/Kolkata')
    head_office_address = models.TextField(blank=True, null=True)
    agents = models.ManyToManyField("Agent",through="ClientsAgent",related_name="companies",blank=True )
    
     # ✅ CENTRAL LOCATION (IMPORTANT)
    location = GenericRelation(Location)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    internal_notes = models.TextField(blank=True, null=True)
    quotation_template = models.ForeignKey(
        "super_admin.Quotation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="template_for_companies"  # ✅ UNIQUE
    )
    
    # contact 
    primary_name=models.CharField(max_length=150,blank=True,null=True,default=""); 
    primary_role=models.CharField(max_length=150,blank=True,null=True,default=""); 
    primary_email=models.EmailField(blank=True,null=True,default=""); 
    primary_phone=models.CharField(max_length=20,blank=True,null=True,default=""); 
    billing_same_as_primary=models.BooleanField(default=False); 
    billing_name=models.CharField(max_length=150,blank=True,null=True,default=""); 
    billing_email=models.EmailField(blank=True,null=True,default=""); 
    billing_phone=models.CharField(max_length=20,blank=True,null=True,default="")

    # Alternate contacts (JSON)
    alternate_contacts = models.JSONField(default=list, blank=True)

   # LegalTaxInfo
    has_gst = models.BooleanField(default=False)
    gstin = models.CharField(max_length=50, blank=True, null=True)
    pan_tax_id = models.CharField(max_length=50, blank=True, null=True)
    tax_country = models.CharField(max_length=100, blank=True, null=True)
    invoice_name_address = models.TextField(blank=True, null=True)
    business_docs = models.FileField(upload_to="business_docs/", blank=True, null=True)
    tds_applicable = models.BooleanField(default=False)
    tds_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)


# BillingRule

    BILLING_CYCLE_CHOICES = (
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    )
    
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default="monthly"
    )

    invoice_due_days = models.IntegerField(default=30)
  
    # 🔹 Slab based billing
    slab_rate = models.ForeignKey(
        SlabRate,
        on_delete=models.PROTECT,
        related_name="billing_rules"
    )

   
    auto_hold_overdue = models.BooleanField(default=False)
    auto_hold_days = models.IntegerField(blank=True, null=True)

    invoice_pattern = models.CharField(max_length=100, default="INV-{FY}-{COMP}-{ID}", help_text="Allowed: {FY}, {YYYY}, {YY}, {MM}, {COMP}, {ID}" )

    default_tax_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

# ContractDocument

    contract_file = models.FileField(upload_to="contracts/", blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    auto_renew = models.BooleanField(default=False)
    terms_conditions = models.TextField(blank=True, null=True)
    
    def delete(self, user=None, *args, **kwargs):
        for loc in self.location.all():
            loc.delete(user=user)
        super().delete(user=user)

    def hard_delete(self):
        for loc in self.location.all():
            loc.hard_delete()
        super().hard_delete()
   

    def __str__(self):
        return f"display_name"
