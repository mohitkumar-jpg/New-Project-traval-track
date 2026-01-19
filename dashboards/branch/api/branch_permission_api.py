from rest_framework.views import APIView
from rest_framework.response import Response
from dashboards.branch.models.branch_permission import BranchPermission


class BranchPermissionAPI(APIView):

    def post(self, request):
        BranchPermission.objects.create(
            branch_id=request.data["branch"],
            user_id=request.data["user"],
            module=request.data["module"],
            submodule=request.data["submodule"],
            can_view=request.data.get("view", False),
            can_create=request.data.get("create", False),
            can_edit=request.data.get("edit", False),
            can_delete=request.data.get("delete", False),
        )

        return Response({"success": True})
