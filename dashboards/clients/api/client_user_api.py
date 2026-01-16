# dashboards/clients/api/client_user_api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from dashboards.clients.models.client_user import ClientUser

User = get_user_model()

class ClientUserCreateAPI(APIView):

    def post(self, request):
        user = User.objects.create_user(
            email=request.data["email"],
            password=request.data["password"],
            user_type="client_user"
        )

        ClientUser.objects.create(
            user=user,
            client_id=request.data["client"],
            is_admin=request.data.get("is_admin", False)
        )

        return Response({"success": True})
