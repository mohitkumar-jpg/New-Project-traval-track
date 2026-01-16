from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator, RegexValidator
from django.contrib.contenttypes.fields import GenericRelation
from dashboards.super_admin.models.base import Location


class Branch(models.Model):

    # ================= BRANCH ADMIN =================
    branch_admin_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admin_of_branch",
        verbose_name="Branch Admin User"
    )

    # ================= BASIC INFO =================
    branch_name = models.CharField(
        max_length=80,
        validators=[MinLengthValidator(3)]
    )
    branch_gst_no = models.CharField(
        max_length=80,
        blank=True,
        null=True
    )
    branch_code = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="inactive"
    )

    timezone = models.CharField(max_length=50, default="Asia/Kolkata")
    operational_start_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    # ================= LOCATION (GenericRelation) =================
    location = GenericRelation(Location)

    # ================= CONTACT =================
    primary_contact_name = models.CharField(max_length=100)
    primary_contact_email = models.EmailField()
    primary_contact_role = models.CharField(max_length=100, blank=True)

    phone_validator = RegexValidator(
        regex=r'^[0-9+\-\s]{8,15}$',
        message="Enter a valid phone number"
    )
    primary_contact_phone = models.CharField(
        max_length=15,
        validators=[phone_validator]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ================= AUTO BRANCH CODE =================
    def _generate_branch_code(self):
        """
        Branch Code Format:
        BR-{CITYCODE}-{0001}
        Example: BR-DEL-0001
        """

        location = self.location.first()  # ✅ GenericRelation → queryset

        if not location or not location.city:
            city_code = "GEN"
        else:
            city_code = location.city[:3].upper()

        last_branch = Branch.objects.filter(
            branch_code__startswith=f"BR-{city_code}"
        ).order_by("-branch_code").first()

        if last_branch:
            try:
                last_no = int(last_branch.branch_code.split("-")[-1])
            except ValueError:
                last_no = 0
        else:
            last_no = 0

        next_no = last_no + 1
        return f"BR-{city_code}-{next_no:04d}"

    def save(self, *args, **kwargs):
        if not self.branch_code:
            self.branch_code = self._generate_branch_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.branch_name} ({self.branch_code})"

    class Meta:
        permissions = [
            ("create_branch", "Can create branch (Super Admin only)"),
            ("assign_branch_admin", "Can assign branch admin"),
            ("manage_branch_users", "Can manage branch users"),
            ("manage_branch_clients", "Can manage branch clients"),
        ]
