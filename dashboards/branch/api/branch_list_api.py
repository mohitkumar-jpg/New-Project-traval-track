from rest_framework.views import APIView
from rest_framework.response import Response
from dashboards.branch.models.branch import Branch


class BranchListAPI(APIView):

    def get(self):
        branches = Branch.objects.all()

        data = []
        for b in branches:
            loc = b.location.first()
            data.append({
                "id": b.id,
                "branch_name": b.branch_name,
                "branch_code": b.branch_code,
                "status": b.status,
                "city": loc.city if loc else None,
                "state": loc.state if loc else None,
            })

        return Response(data)




class BranchDetailAPI(APIView):

    def get(self, pk):
        branch = Branch.objects.get(pk=pk)
        loc = branch.location.first()

        return Response({
            "id": branch.id,
            "branch_name": branch.branch_name,
            "branch_code": branch.branch_code,
            "gst": branch.branch_gst_no,
            "location": {
                "country": loc.country if loc else None,
                "state": loc.state if loc else None,
                "city": loc.city if loc else None,
            }
        })
