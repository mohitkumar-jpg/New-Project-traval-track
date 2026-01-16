# branch/models/branch_permission.py
import django
from django.db import models
from django.conf import settings



class BranchPermission(models.Model):

    branch = models.ForeignKey(
        "branch.Branch",
        on_delete=models.CASCADE,
        related_name="user_permissions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="branch_permissions"
    )

    module = models.CharField(max_length=100)      # Client, Invoice, HR
    submodule = models.CharField(max_length=100)   # Client List, Slab Rate, Attendance

    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_view = models.BooleanField(default=False)

    class Meta:
        unique_together = ("branch", "user", "module", "submodule")

    def __str__(self):
        return f"{self.branch.branch_code} | {self.user.email} | {self.module}"
