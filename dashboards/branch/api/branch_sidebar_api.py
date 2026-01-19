from rest_framework.views import APIView
from rest_framework.response import Response
from dashboards.branch.models.branch_permission import BranchPermission


class BranchSidebarAPI(APIView):

    def get(self, request, branch_id, user_id):

        perms = BranchPermission.objects.filter(
            branch_id=branch_id,
            user_id=user_id,
            can_view=True
        )

        menu = {}

        for p in perms:
            if p.module not in menu:
                menu[p.module] = {
                    "title": p.module,
                    "path": f"/{p.module.lower()}",
                    "permissions": {
                        "view": p.can_view,
                        "create": p.can_create,
                        "edit": p.can_edit,
                        "delete": p.can_delete,
                    },
                    "submodules": []
                }

            menu[p.module]["submodules"].append({
                "title": p.submodule,
                "path": f"/{p.module.lower()}/{p.submodule.replace(' ', '-').lower()}",
                "permissions": {
                    "view": p.can_view,
                    "create": p.can_create,
                    "edit": p.can_edit,
                    "delete": p.can_delete,
                }
            })

        return Response(list(menu.values()))
