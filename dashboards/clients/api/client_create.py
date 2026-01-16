# dashboards/clients/api/client_create.py
from rest_framework.views import APIView
from rest_framework.response import Response
from dashboards.super_admin.models.clients import Clients

class ClientCreateAPI(APIView):

    def post(self, request):
        client = Clients.objects.create(
            display_name=request.data["display_name"],
            legal_company_name=request.data.get("legal_company_name"),
            client_code=request.data["client_code"],
            client_type=request.data["client_type"],
            timezone=request.data.get("timezone", "Asia/Kolkata"),
            slab_rate_id=request.data["slab_rate"],
        )

        return Response({
            "id": client.id,
            "name": client.display_name,
            "message": "Client created"
        })
