from django.db import models
from decimal import Decimal
from datetime import date
from .base import Category,  SoftDeleteModel


class Asset(SoftDeleteModel):
    STATUS_CHOICES = [
    
       ("active", "Active"),
        ("maintenance", "Under Maintenance"),
        ("sold", "Sold"),
        ("retired", "Retired"),
    ]

    DEPRECIATION_METHOD = [
        ("slm", "Straight Line Method"),
        ("wdv", "Written Down Value"),
    ]
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    useful_life_years = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    invoice_id = models.CharField(max_length=100, blank=True, null=True)
    assigned_to = models.ForeignKey("Employee",on_delete=models.SET_NULL,null=True,blank=True,related_name="assigned_assets",)
    purchase_date = models.DateField()
    purchase_value = models.DecimalField(max_digits=12, decimal_places=2)
    residual_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    depreciation_method = models.CharField(max_length=10, choices=DEPRECIATION_METHOD, default="slm")
    location = models.CharField(max_length=150)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    depreciation_start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    vintage = models.CharField(max_length=100, blank=True, null=True)
    warranty_expiry_date = models.DateTimeField(blank=True, null=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)    
    CAPITALISATION = [
        ("capitalized", "Capitalized"),
        ("not_capitalized", "Not Capitalized"),
    ]
    capitalization_status = models.CharField(max_length=20, choices=CAPITALISATION, default="capitalized")
    # remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class AssetDisposal(SoftDeleteModel):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="disposals")
    disposal_date = models.DateField()
    DISPOSAL_CHOICES = [
    
       ("sale", "Sale"),
        ("scrapped", "Scrapped"),
        ("trade", "Trade-in"),
    ]
    disposal_mode = models.CharField(max_length=100, choices=DISPOSAL_CHOICES)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    buyer_details = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disposal of {self.asset.code} on {self.disposal_date}"

class DepreciationScheduler(SoftDeleteModel):
    period_from=models.DateField()
    period_to=models.DateField()
    DISPOSAL_CHOICES = [
       ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]
    schedule=models.CharField(max_length=20, choices=DISPOSAL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by=models.CharField(max_length=150, blank=True, null=True)
    total_depreciation=models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

class Expense(SoftDeleteModel):
    PAYMENT_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("bank", "Bank Transfer"),
        ("upi", "UPI"),
    ]

    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
    ]
    
    branch = models.ForeignKey("branch.Branch",on_delete=models.PROTECT, related_name="expenses")
    expense_date = models.DateField()
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,related_name="expenses")
    # 🔹 Optional but very useful
    employee = models.ForeignKey("Employee",on_delete=models.SET_NULL,null=True,blank=True,related_name="expenses" )
    # 🔹 Same logic as Asset (NO separate table)
    location = models.CharField(max_length=150,blank=True,null=True,help_text="Branch / Office / Site")
    payment_mode = models.CharField(max_length=20,choices=PAYMENT_CHOICES)
    reference_no = models.CharField(max_length=100,blank=True,null=True,help_text="Transaction ID / Cheque No / UPI Ref")
    amount = models.DecimalField(max_digits=12,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="paid")
    description = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to="expenses/",blank=True,null=True,help_text="Bill / Invoice / Receipt")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - ₹{self.amount}"

