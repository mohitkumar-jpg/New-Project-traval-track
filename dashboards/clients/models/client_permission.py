# CLIENT PERMISSION MODEL

from django.db import models
from django.conf import settings

from dashboards.super_admin.models.clients import Clients





class ClientPermission(models.Model):

    client = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name="permissions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_permissions"
    )

    module = models.CharField(max_length=100)
    submodule = models.CharField(max_length=100)

    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ("client", "user", "module", "submodule")

    def __str__(self):
        return f"{self.client.display_name} | {self.user.email} | {self.module}"
