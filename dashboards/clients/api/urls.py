from django.urls import path

from dashboards.clients.api.client_create import ClientCreateAPI
from dashboards.clients.api.client_permission_api import ClientPermissionAPI
from dashboards.clients.api.client_user_api import ClientUserCreateAPI

urlpatterns = [

    # --------------------
    # CLIENT
    # --------------------
    path("create/", ClientCreateAPI.as_view(), name="client_create"),

    # --------------------
    # CLIENT USER
    # --------------------
    path("users/create/", ClientUserCreateAPI.as_view(), name="client_user_create"),

    # --------------------
    # CLIENT PERMISSIONS
    # --------------------
    path("permissions/", ClientPermissionAPI.as_view(), name="client_permission_create"),
]
