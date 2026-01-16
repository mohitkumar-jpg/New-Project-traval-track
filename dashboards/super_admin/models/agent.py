# agent.py

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation


# =========================
# AGENT MODEL
# =========================

class Agent(models.Model):
   
    agent_name = models.CharField(max_length=100)
    agent_email = models.EmailField(unique=True)
    agent_phone_number = models.CharField(max_length=15, unique=True)
    location = GenericRelation("Location")
    
    # --------------------
    # EMPLOYEE
    # --------------------
    employee = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        related_name="agents",
        blank=True,
        null=True
    )

    # --------------------
    # AGENT TYPE
    # --------------------
    AGENT_TYPE_CHOICES = (
        ("individual", "Individual"),
        ("company", "Company"),
        ("channel_partner", "Channel Partner"),
        ("freelancer", "Freelancer"),
        ("employee", "Employee"),
        ("other", "Other"),
    )

    agent_type = models.CharField(max_length=30, choices=AGENT_TYPE_CHOICES)
    other_agent_type = models.CharField(max_length=100, blank=True, null=True)

    # --------------------
    # COMMISSION DETAILS
    # --------------------
    COMMISSION_TYPE_CHOICES = (
        ("percentage", "Percentage"),
        ("flat", "Flat Amount"),
    )

    COMMISSION_TRIGGER_CHOICES = (
        ("deal_closure", "On Deal Closure"),
        ("on_payment_received", "On Payment Received"),
    )

    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES)
    commission_value = models.DecimalField(max_digits=10, decimal_places=2)
    commission_trigger = models.CharField(max_length=30, choices=COMMISSION_TRIGGER_CHOICES)

    # --------------------
    # PAYMENT DETAILS
    # --------------------
    PAYMENT_MODE_CHOICES = (
        ("bank", "Bank Transfer"),
        ("upi", "UPI"),
        ("cash", "Cash"),
    )

    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # --------------------
    # STATUS
    # --------------------
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------
    # VALIDATION
    # --------------------
    def clean(self):

        # Employee agent → employee required
        if self.agent_type == "employee" and not self.employee:
            raise ValidationError({"employee": "Employee is required for Employee agent type."})

        # Individual / Freelancer → employee required
        if self.agent_type in ["individual", "freelancer"] and not self.employee:
            raise ValidationError({"employee": "Employee is required for this agent type."})

        # Other → description required
        if self.agent_type == "other" and not self.other_agent_type:
            raise ValidationError({"other_agent_type": "Please specify agent type."})

    # --------------------
    # AUTO FILL FROM EMPLOYEE
    # --------------------
    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 very important

        if self.agent_type == "employee" and self.employee:
            self.agent_name = self.employee.name
            self.agent_email = self.employee.email
            self.agent_phone_number = self.employee.phone_number

        super().save(*args, **kwargs)

    def __str__(self):
        return self.agent_name


# =========================
# DEAL MODEL
# =========================

class Deal(models.Model):

    # --------------------
    # RELATIONS
    client = models.ForeignKey("super_admin.Clients", on_delete=models.CASCADE, related_name="deals" )
    agent = models.ForeignKey(  "Agent", on_delete=models.SET_NULL, related_name="deals",  blank=True, null=True  )

    # --------------------
    # DEAL DETAILS
    # --------------------
    deal_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Deal value in INR"
    )

    DEAL_TYPE_CHOICES = (
        ("service", "Service"),
        ("product", "Product"),
        ("subscription", "Subscription"),
        ("other", "Other"),
    )

    deal_type = models.CharField(
        max_length=30,
        choices=DEAL_TYPE_CHOICES,
        default="service"
    )

    # --------------------
    # DEAL STATUS
    # --------------------
    DEAL_STATUS_CHOICES = (
        ("lead", "Lead"),
        ("converted", "Converted"),
        ("invoiced", "Invoiced"),
        ("payment_received", "Payment Received"),
        ("cancelled", "Cancelled"),
    )

    deal_status = models.CharField(
        max_length=30,
        choices=DEAL_STATUS_CHOICES,
        default="lead"
    )

    STATUS_FLOW = {
        "lead": ["converted", "cancelled"],
        "converted": ["invoiced", "cancelled"],
        "invoiced": ["payment_received"],
        "payment_received": [],
        "cancelled": [],
    }

    # --------------------
    # COMMISSION TRACKING
    # --------------------
    commission_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )
    commission_calculated = models.BooleanField(default=False)

    # --------------------
    # META
    # --------------------
    deal_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --------------------
    # VALIDATION
    # --------------------
    def clean(self):

        if self.deal_value <= 0:
            raise ValidationError({"deal_value": "Deal value must be greater than zero."})

        if self.pk:
            previous = Deal.objects.get(pk=self.pk)
            if self.deal_status not in self.STATUS_FLOW.get(previous.deal_status, []):
                raise ValidationError(
                    f"Cannot change status from {previous.get_deal_status_display()} "
                    f"to {self.get_deal_status_display()}"
                )

    # --------------------
    # COMMISSION LOGIC
    # --------------------
    def calculate_commission(self):

        if not self.agent:
            return 0

        agent = self.agent

        if agent.commission_type == "percentage":
            return (self.deal_value * agent.commission_value) / 100

        if agent.commission_type == "flat":
            if agent.commission_value > self.deal_value:
                raise ValidationError("Flat commission cannot exceed deal value.")
            return agent.commission_value

        return 0

    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 important

        previous = Deal.objects.get(pk=self.pk) if self.pk else None

        # Commission only on valid status change
        if (
            self.agent
            and not self.commission_calculated
            and previous
            and previous.deal_status != self.deal_status
        ):
            if (
                self.agent.commission_trigger == "deal_closure"
                and self.deal_status == "converted"
            ) or (
                self.agent.commission_trigger == "on_payment_received"
                and self.deal_status == "payment_received"
            ):
                self.commission_amount = self.calculate_commission()
                self.commission_calculated = True

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Deal #{self.id} - ₹{self.deal_value}"


class ClientsAgent(models.Model):

    client = models.ForeignKey(
        "super_admin.Clients",
        on_delete=models.CASCADE,
        related_name="client_agents"
    )

    agent = models.ForeignKey(
        "super_admin.Agent",
        on_delete=models.CASCADE,
        related_name="agent_clients"
    )

    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("client", "agent")

    def __str__(self):
        return f"{self.agent} → {self.client}"
