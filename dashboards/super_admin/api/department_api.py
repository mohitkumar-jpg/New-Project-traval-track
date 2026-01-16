from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from dashboards.super_admin.models.hr import Department


class DepartmentAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = Department.objects.all().values(
            "id", "name", "status", "created_at"
        )

        return Response({
            "status": True,
            "message": "",
            "data": list(data)
        })

    def post(self, request):
        name = request.data.get("name")
        status = request.data.get("status", "active")  # ✅ lowercase

        if not name:
            return Response({
                "status": False,
                "message": "Department name is required",
                "data": []
            }, status=400)

        if Department.objects.filter(name=name).exists():
            return Response({
                "status": False,
                "message": "Department already exists",
                "data": []
            }, status=400)

        dept = Department.objects.create(
            name=name,
            status=status
        )

        return Response({
            "status": True,
            "message": "Department created successfully",
            "data": {
                "id": dept.id,
                "name": dept.name,
                "status": dept.status,
                "created_at": dept.created_at
            }
        })


class DepartmentDetailAPI(APIView):
    permission_classes = [AllowAny]

    def put(self, request, pk):
        try:
            dept = Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return Response({
                "status": False,
                "message": "Department not found",
                "data": []
            }, status=404)

        dept.name = request.data.get("name", dept.name)
        dept.status = request.data.get("status", dept.status)
        dept.save()

        return Response({
            "status": True,
            "message": "Department updated successfully",
            "data": {
                "id": dept.id,
                "name": dept.name,
                "status": dept.status
            }
        })

    def delete(self, request, pk):
        try:
            department = Department.objects.get(pk=pk)
            department.delete(user=request.user)
        except Department.DoesNotExist:
            return Response({
                "status": False,
                "message": "Department not found",
                "data": []
            }, status=404)

        return Response({
            "status": True,
            "message": "Department deleted successfully",
            "data": []
        })
