# client_user.py
from django.db import models
from django.conf import settings
from dashboards.clients.models import Clients

class ClientUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_profile"
    )

    client = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        related_name="users"
    )

    is_admin = models.BooleanField(default=False)  # client admin or staff

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} → {self.client.display_name}"
