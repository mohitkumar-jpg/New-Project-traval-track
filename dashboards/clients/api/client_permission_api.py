# dashboards/clients/api/client_permission_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from dashboards.clients.models.client_permission import ClientPermission

class ClientPermissionAPI(APIView):

    def post(self, request):
        ClientPermission.objects.create(
            client_id=request.data["client"],
            user_id=request.data["user"],
            module=request.data["module"],
            submodule=request.data["submodule"],
            can_view=request.data.get("view", False),
            can_create=request.data.get("create", False),
            can_edit=request.data.get("edit", False),
            can_delete=request.data.get("delete", False),
        )

        return Response({"success": True})
