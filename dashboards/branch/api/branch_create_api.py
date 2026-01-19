from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from dashboards.branch.models.branch import Branch
from dashboards.super_admin.models.base import Location
from django.contrib.contenttypes.models import ContentType


class BranchCreateAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        branch = Branch.objects.create(
            branch_name=request.data["branch_name"],
            branch_gst_no=request.data.get("branch_gst_no"),
            primary_contact_name=request.data["primary_contact_name"],
            primary_contact_email=request.data["primary_contact_email"],
            primary_contact_phone=request.data["primary_contact_phone"],
        )

        # 🔥 GenericRelation correct way
        Location.objects.create(
            content_type=ContentType.objects.get_for_model(Branch),
            object_id=branch.id,
            country=request.data["country"],
            state=request.data["state"],
            city=request.data["city"],
            address=request.data.get("address"),
            zip_code=request.data.get("zip_code"),
        )

        return Response({
            "success": True,
            "branch": {
                "id": branch.id,
                "branch_name": branch.branch_name,
                "branch_code": branch.branch_code
            }
        }, status=201)
